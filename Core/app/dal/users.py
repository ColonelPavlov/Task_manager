async def get_user_by_username(
        db,
        username: str
) -> tuple | None:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT user_id, username FROM users WHERE username = %s", (username,))
        
        return await cursor.fetchone()