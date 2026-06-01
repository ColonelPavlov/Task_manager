from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_connection
from app.schemas.projects import ProjectCreate
from app.dal import projects as projects_dal
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/projects", tags=["Projects"])

security_scheme = HTTPBearer()


# [GET]
@router.get("")
async def get_projects(
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
            
        projects_list = await projects_dal.get_projects(db, current_user_id)
        
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
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        if await projects_dal.project_exists(db, project_data.name, current_user_id):
            raise HTTPException(
                status_code=400,
                detail="Проект с таким названием уже существует"
            )
        
        new_project_id = await projects_dal.create_project(db, current_user_id, project_data.name)

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
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        if not await projects_dal.delete_project(db, name, current_user_id):
            raise HTTPException(
                status_code=404,
                detail="Проект не найден или у вас нет прав на его удаление"
            )
            
        return {
            "status": "success",
            "message": f"Проект '{name}' успешно удалён из архива Murkoff сотрудником {current_username}."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
