from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_connection
from app.schemas.tags import TagCreate
from app.dal import tags as tags_dal
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/tags", tags=["Tags"])
security_scheme = HTTPBearer()


# [GET]
@router.get("")
async def get_tags(
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        tags_list = await tags_dal.get_tags(db, current_user_id)
        
        return {
            "status": "success",
            "requested_by": current_username,
            "tags": tags_list
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [POST]
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        if await tags_dal.tag_exists(db, tag_data.name, current_user_id):
            raise HTTPException(
                status_code=400,
                detail="Тег с таким названием уже существует"
            )
        
        new_tag_id = await tags_dal.create_tag(db, current_user_id, tag_data.name, tag_data.color)
            
        return {
            "status": "success",
            "message": f"Тег '{tag_data.name}' успешно создан агентом {current_username}!",
            "tag": {
                "id": new_tag_id,
                "name": tag_data.name,
                "color": tag_data.color
            }
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [DELETE]
@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        if not await tags_dal.delete_tag(db, tag_id, current_user_id):
            raise HTTPException(
                status_code=404,
                detail="Тег не найден или у вас нет прав на его удаление"
            )
            
        return {
            "status": "success",
            "message": f"Тег ID {tag_id} успешно удалён из архива сотрудником {current_username}."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
