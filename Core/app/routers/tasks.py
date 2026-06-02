from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_connection
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.dal import tasks as tasks_dal
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
security_scheme = HTTPBearer()

# [POST]
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        new_task_id = await tasks_dal.create_task(
            db, current_user_id,
            task_data.task_number, task_data.description, task_data.deadline,
            task_data.priority, task_data.status or "new",
            task_data.project_id, task_data.tag_id
        )
            
        return {
            "status": "success",
            "message": f"Задача успешно создана сотрудником {current_username}!",
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
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [GET]
@router.get("")
async def read_tasks(
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        tasks_list = await tasks_dal.get_tasks(db, current_user_id)
            
        return {
            "status": "success",
            "requested_by": current_username,
            "tasks": tasks_list
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [PUT]
@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
       
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        fields = task_data.model_dump(exclude_unset=True)
            
        if not fields:
            raise HTTPException(
                status_code=400,
                detail="Нет данных для обновления"
            )
            
        updated_row = await tasks_dal.update_task(db, task_id, current_user_id, fields)
            
        if not updated_row:
            raise HTTPException(
                status_code=404,
                detail="Задача не найдена"
            )
            
        return {
            "status": "success",
            "message": f"Задача успешно обновлена сотрудником {current_username}",
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
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [DELETE]
@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        if not await tasks_dal.delete_task(db, task_id, current_user_id):
            raise HTTPException(
                status_code=404,
                detail="Задача не найдена"
            )
            
        return {
            "status": "success",
            "message": f"Задача ID {task_id} успешно удалена сотрудником {current_username}."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
