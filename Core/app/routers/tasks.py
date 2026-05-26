from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer
from typing import List

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
security_scheme = HTTPBearer()

# 1. [POST] — Создание задачи с возвратом ПОЛНОГО объекта task
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            # Пишем ВСЕ поля в базу Егора, включая новые связи проектов и тегов
            insert_query = """
                INSERT INTO tasks (user_id, task_number, description, deadline, priority, status, project_id, tag_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            await cursor.execute(insert_query, (
                current_user_id, 
                task_data.task_number, 
                task_data.description, 
                task_data.deadline, 
                task_data.priority, 
                task_data.status if task_data.status else "new",
                task_data.project_id,
                task_data.tag_id
            ))
            new_task_id = cursor.lastrowid
            
        # Возвращаем СТРОГО то, что ждёт фронтенд: result.data.task
        return {
            "status": "success",
            "message": "Задача успешно создана!",
            "data": {
                "task": {
                    "task_id": new_task_id,
                    "user_id": current_user_id,
                    "task_number": task_data.task_number,
                    "description": task_data.description,
                    "deadline": task_data.deadline.isoformat() if task_data.deadline else None,
                    "priority": task_data.priority,
                    "status": task_data.status if task_data.status else "new",
                    "project_id": task_data.project_id,
                    "tag_id": task_data.tag_id
                }
            }
        }
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


# 2. [GET] — Чтение задач (Возвращаем плоские данные, совместимые с фронтом)
@router.get("")
async def read_tasks(
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("""
                SELECT task_id, user_id, task_number, description, deadline, priority, status, created_at, updated_at, project_id, tag_id 
                FROM tasks WHERE user_id = %s
            """, (current_user_id,))
            raw_tasks = await cursor.fetchall()
        
        tasks_list = []
        for row in raw_tasks:
            tasks_list.append({
                "task_id": row[0],
                "user_id": row[1],
                "task_number": row[2],
                "description": row[3],
                "deadline": row[4].isoformat() if row[4] else None,
                "priority": row[5],
                "status": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
                "project_id": row[9],  # Отдаем ID проекта для фильтрации
                "tag_id": row[10]      # Отдаем ID тега для рендера плашек
            })
            
        return {
            "status": "success",
            "requested_by": current_username,
            "tasks": tasks_list
        }
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


# 3. [PUT] — Мощное ДИНАМИЧЕСКОЕ обновление ВСЕХ полей (включая статус при перетаскивании карточки!)
@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        # Динамически собираем SQL-запрос только из тех полей, которые прислал фронт (exclude_unset=True)
        update_fields = []
        update_values = []
        
        for field, value in task_data.model_dump(exclude_unset=True).items():
            update_fields.append(f"`{field}` = %s")
            update_values.append(value)
            
        if not update_fields:
            raise HTTPException(status_code=400, detail="Нет данных для обновления")
            
        # Добавляем параметры для WHERE
        update_values.extend([task_id, current_user_id])
        sql_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE task_id = %s AND user_id = %s"
        
        async with db.cursor() as cursor:
            # Выполняем точечный апдейт в базу Егора
            await cursor.execute(sql_query, tuple(update_values))
            
            # Сразу же достаем свежие данные из базы, чтобы вернуть их фронту!
            await cursor.execute("""
                SELECT task_id, user_id, task_number, description, deadline, priority, status, project_id, tag_id 
                FROM tasks WHERE task_id = %s AND user_id = %s
            """, (task_id, current_user_id))
            updated_row = await cursor.fetchone()
            
        if not updated_row:
            raise HTTPException(status_code=404, detail="Задача не найдена")
            
        # Возвращаем СТРОГО структуру result.data.task, которую требует фронтенд!
        return {
            "status": "success",
            "message": "Задача успешно обновлена",
            "data": {
                "task": {
                    "task_id": updated_row[0],
                    "user_id": updated_row[1],
                    "task_number": updated_row[2],
                    "description": updated_row[3],
                    "deadline": updated_row[4].isoformat() if updated_row[4] else None,
                    "priority": updated_row[5],
                    "status": updated_row[6],
                    "project_id": updated_row[7],
                    "tag_id": updated_row[8]
                }
            }
        }
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


# 4. [DELETE] — Удаление задачи
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
                raise HTTPException(status_code=404, detail="Задача не найдена")
                
            await cursor.execute("DELETE FROM tasks WHERE task_id = %s AND user_id = %s", (task_id, current_user_id))
            
        return {
            "status": "success",
            "message": f"Задача ID {task_id} успешно удалена сотрудником {current_username}."
        }
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
