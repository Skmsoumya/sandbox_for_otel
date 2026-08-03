from fastapi import FastAPI, HTTPException
from utils.redis import redis_client, TTL_SECONDS
from utils.db import get_connection
from models import ItemCreate, Item
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert items into the DB
            cur.execute(
                """
                INSERT INTO items (name, quantity)
                VALUES (%s, %s)
                RETURNING id, name, quantity
                """,
                (item.name, item.quantity),
            )
            row = cur.fetchone()
        conn.commit()
        item_id = row[0]
        name = row[1]
        quantity = row[2]
        # Set the new item to the cache.
        redis_client.set(f"item:{item_id}", json.dumps(row), ex=TTL_SECONDS)
        # invalidate the items list cache.
        redis_client.delete("items:all")

    if row is None:
        raise HTTPException(status_code=500, detail="Insert failed")

    return Item(id=row[0], name=name, quantity=quantity)


@app.get("/items", response_model=list[Item])
async def list_items():
    raw_from_cache = redis_client.get("items:all")
    # if cache is empty, either due to new items being added or cache expiry, 
    # we pull from db otherwise we serve from cache
    if raw_from_cache:
        items = json.loads(raw_from_cache) if raw_from_cache else None
        return [Item(id=r["id"], name=r["name"], quantity=r["quantity"]) for r in items]
    else:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, quantity FROM items ORDER BY id")
                rows = cur.fetchall()
        items = [Item(id=r[0], name=r[1], quantity=r[2]) for r in rows]
        redis_client.set("items:all", json.dumps([item.model_dump() for item in items]), ex=TTL_SECONDS)
        return items