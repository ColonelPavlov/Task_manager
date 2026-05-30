from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.schemas.projects import ProjectCreate
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/projects", tags=["Projects"])

security_scheme = HTTPBearer()


# [GET]
@router.get("")
async def get_projects(
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT project_id, name FROM projects WHERE user_id = %s", (current_user_id,))
            raw_projects = await cursor.fetchall()
            
        projects_list = [{"project_id": row[0], "name": row[1]} for row in raw_projects]
        
        return {
            "status": "success",
            "requested_by": current_username,
            "projects": projects_list
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [POST]
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT project_id FROM projects WHERE name = %s AND user_id = %s", (project_data.name, current_user_id))
            if await cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Проект с таким названием уже существует"
                )
                
            insert_query = "INSERT INTO projects (user_id, name) VALUES (%s, %s)"
            await cursor.execute(insert_query, (current_user_id, project_data.name))

            new_project_id = cursor.lastrowid

        return {
            "status": "success",
            "message": f"Проект '{project_data.name}' успешно созданагентом {current_username}!",
            "project_id": new_project_id
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [DELETE]
@router.delete("/{name}")
async def delete_project(
    name: str,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT project_id FROM projects WHERE name = %s AND user_id = %s", (name, current_user_id))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail="Проект не найден или у вас нет прав на его удаление"
                )
                
            await cursor.execute("DELETE FROM projects WHERE name = %s AND user_id = %s", (name, current_user_id))
            
        return {
            "status": "success",
            "message": f"Проект '{name}' успешно удалён из архива Murkoff сотрудником {current_username}."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
