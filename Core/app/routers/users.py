from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer


router = APIRouter(prefix="/api/users", tags=["Users"])

security_scheme = HTTPBearer()


# [GET]
@router.get("/{username}")
async def get_user_profile(
    username: str,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:

        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT user_id, username, role FROM users WHERE username = %s", (username,))
            user_data = await cursor.fetchone()
            
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail="Сотрудник Murkoff не найден в системе"
            )
            
        real_role = user_data[2] if user_data[2] else "user"
        
        return {
            "status": "success",
            "username": user_data[1],
            "role": "Администратор Murkoff" if real_role == "admin" else "Сотрудник Murkoff",
            "clearance_level": "Максимальный допуск" if real_role == "admin" else "Ограниченный допуск"
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )

# [GET]
@router.get("")
async def get_all_users(
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT user_id, username, role FROM users")
            raw_users = await cursor.fetchall()
            
        users_list = []
        for row in raw_users:
            users_list.append({
                "user_id": row[0],
                "username": row[1],
                "role": row[2] if row[2] else "user"
            })
            
        return {
            "status": "success",
            "requested_by": current_username,
            "users": users_list
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )

# [PUT]
@router.put("/{username}/make-admin")
async def make_admin(
    username: str,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail="Пользователь не найден"
                )
            
            await cursor.execute("UPDATE users SET role = 'admin' WHERE username = %s", (username,))
            
        return {
            "status": "success",
            "message": f"Пользователь '{username}' успешно назначен администратором."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )


# [DELETE]
@router.delete("/{username}")
async def delete_user(
    username: str,
    db = Depends(get_db),
    token = Depends(security_scheme)
) -> dict:
    try:
        
        current_user_id, current_username = await get_current_user_double_check(db=db, credentials=token)
        
        if current_username == username:
            raise HTTPException(
                status_code=400,
                detail="Вы не можете удалить самого себя"
            )
            
        async with db.cursor() as cursor:
            await cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail="Пользователь не найден"
                )
                
            await cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            
        return {
            "status": "success",
            "message": f"Сотрудник '{username}' безвозвратно удалён."
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
