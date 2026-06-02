async def get_tags(
        db,
        user_id: int
) -> dict:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT tag_id AS id, name, color FROM tags WHERE user_id = %s", (user_id,))
        rows = await cursor.fetchall()
    
    return [{"id": r[0], "name": r[1], "color": r[2]} for r in rows]


async def tag_exists(
        db,
        name: str,
        user_id: int
) -> bool:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT tag_id FROM tags WHERE name = %s AND user_id = %s", (name, user_id))
        
        return await cursor.fetchone() is not None


async def create_tag(
        db,
        user_id: int,
        name: str,
        color: str
) -> int:
    async with db.cursor() as cursor:
        
        await cursor.execute("INSERT INTO tags (user_id, name, color) VALUES (%s, %s, %s)", (user_id, name, color))
        
        return cursor.lastrowid


async def delete_tag(
        db,
        tag_id: int,
        user_id: int
) -> bool:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT tag_id FROM tags WHERE tag_id = %s AND user_id = %s", (tag_id, user_id))
        
        if not await cursor.fetchone():
            return False
        
        await cursor.execute("DELETE FROM tags WHERE tag_id = %s AND user_id = %s", (tag_id, user_id))
        
        return True