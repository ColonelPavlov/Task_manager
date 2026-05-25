from fastapi import APIRouter
from app.schemas.tasks import TaskCreate, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


# [C]REATE
@router.post("")
def create_task(task_data: TaskCreate):
    # TODO: Тут будет SQL: INSERT INTO tasks (title, description) VALUES (...) и прочий ужас
    return {
        "status": "success",
        "message": f"Задача '{task_data.title}' успешно создана в системе Murkoff!",
        "id": 101  # Пока что фейковый ID, нужна база данных
    }

# [R]EAD
@router.get("")
def read_tasks():
    # TODO: Тут будет SQL: SELECT * FROM tasks;
    return [
        {"id": 101, "title": "Проверить статус Реагентов с последнего испытания", "status": "new", "description": "Срочно"},
        {"id": 102, "title": "Эксперимент над новым Экс-Попом", "status": "in_progress", "description": "Секретно"}
    ]

# [U]PDATE
@router.put("/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    # TODO: Тут будет SQL: UPDATE tasks SET status = %s WHERE id = %s;
    return {
        "status": "success",
        "message": f"Статус задачи №{task_id} успешно изменён на '{task_data.status}'"
    }

# [D]ELETE
@router.delete("/{task_id}")
def delete_task(task_id: int):
    # TODO: Тут будет SQL: DELETE FROM tasks WHERE id = %s;
    return {
        "status": "success",
        "message": f"Задача №{task_id} удалена из архива"
    }
