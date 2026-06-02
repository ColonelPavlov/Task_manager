async def get_projects(
        db,
        user_id: int
) -> dict:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT project_id, name FROM projects WHERE user_id = %s", (user_id,))
        rows = await cursor.fetchall()
    
    return [{"project_id": r[0], "name": r[1]} for r in rows]


async def project_exists(
        db,
        name: str,
        user_id: int
) -> bool:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT project_id FROM projects WHERE name = %s AND user_id = %s", (name, user_id))
        
        return await cursor.fetchone() is not None


async def create_project(
        db,
        user_id: int,
        name: str
) -> int:
    async with db.cursor() as cursor:
        
        await cursor.execute("INSERT INTO projects (user_id, name) VALUES (%s, %s)", (user_id, name))
        
        return cursor.lastrowid


async def delete_project(
        db,
        name: str,
        user_id: int
) -> bool:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT project_id FROM projects WHERE name = %s AND user_id = %s", (name, user_id))
        
        if not await cursor.fetchone():
            return False
        
        await cursor.execute("DELETE FROM projects WHERE name = %s AND user_id = %s", (name, user_id))
        
        return True