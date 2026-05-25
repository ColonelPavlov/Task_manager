from fastapi import APIRouter
from app.schemas.auth import UserRegister

router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/register")
def register_user(user_data: UserRegister):
    # TODO: for [Backend(Я) + Data Engineer(Егор)] Когда подключим базу данных, переписать логику:
    # 1. Отправлять сырой пароль в сервис Supporting(Flask) для хэширования.
    # 2. Сохранять username и полученный пароль-хэш в базу данных через чистый SQL или как там (Не разбираюсь).
    # 3. Реализовать генерацию JWT-токена после успешной записи.

    # ВНИМАНИЕ: Я знаю, что сырые пароли никогда не возвращаются в ответе!
    # Сейчас это сделано временно для отладки, пока нет базы данных и механизма JWT.

    return {
        "status": "success",
        "message": f"Регистрация пользователя {user_data.username} прошла успешно!",
        "debug_info": {
            "received_username": user_data.username,
            "received_password": user_data.password
        }
    }

@router.post("/login")
def login_user(user_data: UserRegister):
    # TODO: [Backend(Я)] Когда подключим базу данных:
    # 1. Найти юзера в базе по user_data.username.
    # 2. Сверить хэш пароля.
    # 3. Если всё ок - сгенерировать реальный JWT-токен.
    
    if user_data.username == "user" and user_data.password == "user_usual_password_1337":
        return {
            "status": "success", 
            "message": "Вход выполнен успешно!", 
            "token": "fake_jwt_token_for_user"
        }
    elif user_data.username == "admin" and user_data.password == "admin_top_secret_password_1488":
        return {
            "status": "success", 
            "message": "Вход выполнен успешно!", 
            "token": "fake_jwt_token_for_admin"
        }
    
    return {"status": "denied", "message": "Неверный логин или пароль"}

@router.post("/users/{username}/refresh-token")
def refresh_user_token(username: str):
    # TODO: Логика обновления JWT-токена будет в будущем
    return {
        "status": "success",
        "message": f"Токен для пользователя {username} успешно обновлен!",
        "new_token": "new_fake_jwt_token_777_azino_tri_topora"
    }
