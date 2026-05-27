import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def get_db():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    try:
        yield conn
    finally:
        await conn.close()
