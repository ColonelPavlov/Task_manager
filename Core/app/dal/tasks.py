async def create_task(
        db,
        user_id: int,
        task_number, description, deadline, priority, status, project_id, tag_id
) -> int:
    async with db.cursor() as cursor:
        
        await cursor.execute("INSERT INTO tasks (user_id, task_number, description, deadline, priority, status, project_id, tag_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, task_number, description, deadline, priority, status, project_id, tag_id))
        
        return cursor.lastrowid

async def get_tasks(
        db,
        user_id: int
) -> dict:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT task_id, user_id, task_number, description, deadline, priority, status, created_at, updated_at, project_id, tag_id FROM tasks WHERE user_id = %s",
            (user_id,))
        
        rows = await cursor.fetchall()
    
    return [
        {
            "task_id": r[0], "user_id": r[1], "task_number": r[2], "description": r[3],
            "deadline": r[4].isoformat() if r[4] else None,
            "priority": r[5], "status": r[6],
            "created_at": r[7].isoformat() if r[7] else None,
            "updated_at": r[8].isoformat() if r[8] else None,
            "project_id": r[9], "tag_id": r[10]
        }
        for r in rows
    ]

async def update_task(
        db,
        task_id: int,
        user_id: int,
        fields: dict
) -> tuple | None:
    update_parts = [f"`{field}` = %s" for field in fields]
    values = list(fields.values()) + [task_id, user_id]
    
    async with db.cursor() as cursor:
       
        await cursor.execute(f"UPDATE tasks SET {', '.join(update_parts)} WHERE task_id = %s AND user_id = %s", tuple(values))
        
        await cursor.execute("SELECT task_id, user_id, task_number, description, deadline, priority, status, project_id, tag_id FROM tasks WHERE task_id = %s AND user_id = %s",
            (task_id, user_id))
        
        return await cursor.fetchone()

async def delete_task(
        db,
        task_id: int,
        user_id: int
) -> bool:
    async with db.cursor() as cursor:
        
        await cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s AND user_id = %s", (task_id, user_id))
        
        if not await cursor.fetchone():
            return False
        
        await cursor.execute("DELETE FROM tasks WHERE task_id = %s AND user_id = %s", (task_id, user_id))
        
        return True