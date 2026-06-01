from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db_connection
from app.dal import users as users_dal
from app.auth_utils import get_current_user_double_check
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/users", tags=["Users"])
security_scheme = HTTPBearer()


# [GET]
@router.get("/{username}")
async def get_user_profile(
    username: str,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:
    try:

        await get_current_user_double_check(db=db, credentials=token)
        
        user_data = await users_dal.get_user_by_username(db, username)
            
        return {
            "status": "success",
            "username": user_data
        }
    
    except HTTPException: raise
    except Exception as e: raise HTTPException(
        status_code=500,
        detail=str(e)
    )
