from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.database import get_db_connection
from app.schemas.auth import UserRegister
from app.dal import auth as auth_dal
from app.auth_utils import hash_password, verify_password, create_access_token
from app.auth_utils import get_current_user_double_check, create_access_token

router = APIRouter(prefix="/api", tags=["Authentication"])
security_scheme = HTTPBearer()


@router.post("/register")
async def register_user(
    user_data: UserRegister,
    db = Depends(get_db_connection)
) -> dict:
    try:

        await auth_dal.create_user(db, user_data.username, hash_password(user_data.password))

        return {
            "status": "success",
            "message": f"Пользователь {user_data.username} успешно добавлен в систему Murkoff Corporation! Пароль захеширован."
            }

    except Exception as e:
        error_msg = str(e)

        if "Duplicate entry" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сотрудник с именем '{user_data.username}' уже существует!"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных при регистрации: {error_msg}"
        )

@router.post("/login")
async def login_user(
    user_data: UserRegister,
    db = Depends(get_db_connection)
) -> dict:
    try:
        
        db_user = await auth_dal.get_user_credentials(db, user_data.username)
        
        if not db_user or not verify_password(user_data.password, db_user[1]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # Распаковка кортежа из базы данных
        db_username, db_password_hash = db_user
        # Проверка на совпадение сырого пароля и хэша из базы данных
        if not verify_password(user_data.password, db_password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # После совпадения сырого пароля с хэшем идёт, идёт генерация настоящего JWT-токена. Идёт зашивание в токен имя пользователя
        token_data = {"sub": db_username}
        access_token = create_access_token(data=token_data)
        return {
            "status": "success",
            "message": f"Вход для {db_username} выполнен успешно!",
            "token_type": "bearer",
            "access_token": access_token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных при входе: {str(e)}"
        )

@router.post("/users/{username}/refresh-token")
async def refresh_user_token(
    username: str,
    db = Depends(get_db_connection),
    token = Depends(security_scheme)
) -> dict:

    current_user = await get_current_user_double_check(db=db, credentials=token)

    # Проверка совпадает ли имя из токена с тем, что ввели в пути URL
    if username != current_user[1]: # Нас интересует именно username из кортежа (user_id, username), который возвращает get_current_user_double_check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете обновить токен другого сотрудника!"
        )

    # Если всё совпадает, то генерируется свежий JWT-токен на 12 часов
    token_data = {"sub": username}
    new_access_token = create_access_token(data=token_data)

    return {
        "status": "success",
        "message": f"Сессия для пользователя {username} успешно продлена в терминале Murkoff!",
        "token_type": "bearer",
        "access_token": new_access_token
    }
