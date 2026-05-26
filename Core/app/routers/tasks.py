from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.database import get_db
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.auth_utils import get_current_user_double_check

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
security_scheme = HTTPBearer()


# [C]REATE
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:

        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)

        async with db.cursor() as cursor:
            insert_query = "INSERT INTO tasks (user_id, task_number, description, deadline, priority, status) VALUES (%s, %s, %s, %s, %s, %s)"
            await cursor.execute(insert_query, (
                current_user_id, 
                task_data.task_number, 
                task_data.description, 
                task_data.deadline, 
                task_data.priority, 
                task_data.status
            ))
        
        return {
            "status": "success",
            "message": f"Задача №'{task_data.task_number}' успешно создана сотрудником {current_username}!"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных при создании задачи: {str(e)}"
        )

# [R]EAD
@router.get("")
async def read_tasks(
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:

        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)

        async with db.cursor() as cursor:
            await cursor.execute("SELECT task_id, user_id, task_number, description, deadline, priority, status, created_at, updated_at FROM tasks WHERE user_id = %s", (current_user_id,))
            raw_tasks = await cursor.fetchall()

        tasks_list = []
        for row in raw_tasks:
            tasks_list.append({
                "task_id": row[0],
                "user_id": row[1],
                "task_number": row[2],
                "description": row[3],
                "deadline": row[4].isoformat() if row[4] else None,   # Безопасный перевод в str
                "priority": row[5],
                "status": row[6],
                "created_at": row[7].isoformat() if row[7] else None, # Безопасный перевод в str
                "updated_at": row[8].isoformat() if row[8] else None  # Безопасный перевод в str
            })

        return {
            "status": "success",
            "requested_by": current_username,
            "tasks": tasks_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных при получении списка задач: {str(e)}"
        )
    
# [U]PDATE
@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:

        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)

        async with db.cursor() as cursor:
            await cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s AND user_id = %s", (task_id, current_user_id))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Задача не найдена или у вас нет прав на её изменение"
                )

            update_query = "UPDATE tasks SET task_number = %s WHERE task_id = %s"
            await cursor.execute(update_query, (task_data.task_number, task_id))

        return {
            "status": "success",
            "message": f"Номер задачи ID {task_id} успешно изменён сотрудником {current_username}."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных при обновлении задачи: {str(e)}"
        )

# [D]ELETE
@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:

        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)

        async with db.cursor() as cursor:
            await cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s AND user_id = %s", (task_id, current_user_id))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Задача не найдена или у вас нет прав на её удаление"
                )
            
            await cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))

        return {
            "status": "success",
            "message": f"Задача №{task_id} безвозвратно удалена из архива Murkoff сотрудником {current_username}."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных при удалении задачи: {str(e)}"
        )