from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.database import get_db
from app.schemas.auth import UserRegister
from app.auth_utils import hash_password, verify_password, create_access_token
from app.auth_utils import get_current_user_double_check, create_access_token

router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/register")
async def register_user(user_data: UserRegister, db = Depends(get_db)) -> dict:
    try:
        # Хэшируем сырой пароль пользователя перед отправкой в базу данных
        secure_password_hash = hash_password(user_data.password)

        async with db.cursor() as cursor:
            # Чистый SQL запрос на добавление строки
            insert_query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
            await cursor.execute(insert_query, (user_data.username, secure_password_hash))

        return {
            "status": "success",
            "message": f"Пользователь {user_data.username} успешно добавлен в систему Murkoff Corporation! Пароль захеширован."
            }

    except Exception as e:
        error_msg = str(e)
        # Перехватываем дубликат юзернейма, чтобы выдать красивый статус 400 вместо падения сервера
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
async def login_user(user_data: UserRegister, db = Depends(get_db)) -> dict:
    try:
        async with db.cursor() as cursor:
           # Идёт поиск пользователя в базе данных по его username
           select_query = "SELECT username, password_hash FROM users WHERE username = %s"
           await cursor.execute(select_query, (user_data.username,))
           db_user = await cursor.fetchone()
        # Если пользователя не нашлось в username
        if not db_user:
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

security_scheme = HTTPBearer()

@router.post("/users/{username}/refresh-token")
async def refresh_user_token(username: str, db = Depends(get_db), token = Depends(security_scheme)) -> dict:
    # Запуск Double Check токена
    current_user = await get_current_user_double_check(db=db, credentials=token)

    # Проверка совпадает ли имя из токена с тем, что ввели в пути URL
    if username != current_user:
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
