from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в терминал Murkoff Corporation"}
    
class UserRegister(BaseModel):
    username: str
    password: str

@app.post("/api/register")
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

@app.post("/api/login")
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

@app.get("/api/users/{username}")
def get_user_profile(username: str):
    # TODO: [Backend(Я)] Роут должен быть защищён! 
    # Сюда встанет проверка JWT-токена из заголовков запроса.
    
    # Нам сказали "любой контекст", мы сделаем всё в стиле Murkoff Corporation))
    if username == "user":
        return {
            "status": "success",
            "username": username,
            "role": "Сотрудник Murkoff",
            "clearance_level": "Ограниченный допуск",
            "assigned_project": "None"
        }
    
    return {
        "status": "success",
        "username": username,
        "role": "Администратор Murkoff",
        "clearance_level": "Максимальный допуск",
        "assigned_project": "Управление исследовательским центром Sinyala"
    }

@app.post("/api/users/{username}/refresh-token")
def refresh_user_token(username: str):
    # TODO: Логика обновления JWT-токена будет в будущем
    return {
        "status": "success",
        "message": f"Токен для пользователя {username} успешно обновлен!",
        "new_token": "new_fake_jwt_token_777_azino_tri_topora"
    }

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

class TaskUpdate(BaseModel):
    status: str

# [C]REATE
@app.post("/api/tasks")
def create_task(task_data: TaskCreate):
    # TODO: Тут будет SQL: INSERT INTO tasks (title, description) VALUES (...) и прочий ужас
    return {
        "status": "success",
        "message": f"Задача '{task_data.title}' успешно создана в системе Murkoff!",
        "id": 101  # Пока что фейковый ID, нужна база данных
    }

# [R]EAD
@app.get("/api/tasks")
def read_tasks():
    # TODO: Тут будет SQL: SELECT * FROM tasks;
    return [
        {"id": 101, "title": "Проверить статус Реагентов с последнего испытания", "status": "new", "description": "Срочно"},
        {"id": 102, "title": "Эксперимент над новым Экс-Попом", "status": "in_progress", "description": "Секретно"}
    ]

# [U]PDATE
@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    # TODO: Тут будет SQL: UPDATE tasks SET status = %s WHERE id = %s;
    return {
        "status": "success",
        "message": f"Статус задачи №{task_id} успешно изменён на '{task_data.status}'"
    }

# [D]ELETE
@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    # TODO: Тут будет SQL: DELETE FROM tasks WHERE id = %s;
    return {
        "status": "success",
        "message": f"Задача №{task_id} удалена из архива"
    }