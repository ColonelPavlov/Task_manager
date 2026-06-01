async def create_user(
        db,
        username: str,
        password_hash: str
) -> None:
    async with db.cursor() as cursor:
        
        await cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))


async def get_user_credentials(
        db,
        username: str
) -> tuple | None:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
        
        return await cursor.fetchone()