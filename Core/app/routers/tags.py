from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.schemas.tags import TagCreate
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/tags", tags=["Tags"])

security_scheme = HTTPBearer()


# [GET]
@router.get("")
async def get_tags(
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT tag_id AS id, name, color FROM tags WHERE user_id = %s", (current_user_id,))
            raw_tags = await cursor.fetchall()
            
        tags_list = []
        for row in raw_tags:
            tags_list.append({
                "id": row[0],
                "name": row[1],
                "color": row[2]
            })
            
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
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT tag_id FROM tags WHERE name = %s AND user_id = %s", (tag_data.name, current_user_id))
            if await cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Тег с таким названием уже существует"
                )
                
            insert_query = "INSERT INTO tags (user_id, name, color) VALUES (%s, %s, %s)"
            await cursor.execute(insert_query, (current_user_id, tag_data.name, tag_data.color))
            
            # Забираем ID, который только что сгенерировала MySQL
            new_tag_id = cursor.lastrowid
            
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
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT tag_id FROM tags WHERE tag_id = %s AND user_id = %s", (tag_id, current_user_id))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail="Тег не найден или у вас нет прав на его удаление"
                )
                
            await cursor.execute("DELETE FROM tags WHERE tag_id = %s AND user_id = %s", (tag_id, current_user_id))
            
        return {
            "status": "success",
            "message": f"Тег ID {tag_id} успешно удалён из архива сотрудником {current_username}."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
