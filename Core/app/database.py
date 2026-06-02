import os
import aiomysql
from dotenv import load_dotenv

load_dotenv()

# Функция, которая будет выдавать роутам чистое асинхронное соединение с MySQL
async def get_db_connection():
    connection = await aiomysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "change_me"),
        password=os.getenv("DB_PASS", "change_me"),
        db=os.getenv("DB_NAME", "change_me"),
        autocommit=True
    )
    try:
        yield connection
    finally:
        connection.close()