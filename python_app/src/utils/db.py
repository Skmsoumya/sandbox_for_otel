import psycopg
import os
from psycopg_pool import ConnectionPool

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

conninfo = psycopg.conninfo.make_conninfo(
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    dbname=POSTGRES_DB,
)

pool = ConnectionPool(conninfo=conninfo, min_size=1, max_size=2, open=True)

def get_connection():
    return pool.connection()


# I am keeping it simple for the demo, we will just create a table here with a schema. 
def initialize_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL DEFAULT 0
                );
            """
            cur.execute(query)
        conn.commit()

# initiliize the db upon load.
initialize_db()