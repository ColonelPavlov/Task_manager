from fastapi import APIRouter

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/{username}")
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