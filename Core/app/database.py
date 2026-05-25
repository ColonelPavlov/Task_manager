import aiomysql
from app.config import settings

# Функция, которая будет выдавать роутам чистое асинхронное соединение с MySQL
async def get_db():
    connection = await aiomysql.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        user=settings.DB_USER,
        password=settings.DB_PASS,
        db=settings.DB_NAME,
        autocommit=True  # Чтобы INSERT/UPDATE запросы сразу сохранялись в базе данных
    )
    try:
        yield connection
    finally:
        connection.close()