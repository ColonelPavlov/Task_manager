from pydantic import BaseModel

# Cхема проверяет, то ли прислал пользователь при регистрации или входе
class UserRegister(BaseModel):
    username: str
    password: str