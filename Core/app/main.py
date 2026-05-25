from fastapi import FastAPI
from app.routers import auth, users, tasks

app = FastAPI(
    title="Terminal Murkoff Corporation",
    description="Система управления исследовательскими центрами",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в терминал Murkoff Corporation"}
    