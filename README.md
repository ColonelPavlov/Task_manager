# Murkoff Task Manager 📋

**Murkoff Task Manager** — секретный терминал учёта задач и контроля сотрудников Murkoff Corporation. Full Stack web-приложение с элементами микросервисной архитектуры, разработанное в рамках курса Архитектура информационных систем.

---

# Основные возможности ✨

- Kanban-доска с drag-and-drop и четырьмя статусами задач;
- создание, редактирование и удаление задач;
- приоритеты (low / medium / high) и дедлайны;
- группировка задач по проектам и тегам;
- JWT авторизация с возможностью обновления токена;
- аналитическая панель с графиками по задачам текущего пользователя.

---

# Архитектура 🏗️

```text
Браузер (Vanilla JS + Bootstrap)
        ↓               ↓
FastAPI (8000)     Flask (5001)
        ↓               ↓
          MySQL Database
```


Два независимых backend-сервиса. Фронт обращается к каждому напрямую.

---

# Core Service — FastAPI ⚡

Основной сервис. Отвечает за:
- регистрацию и авторизацию пользователей;
- JWT (генерация, валидация, обновление);
- CRUD задач, проектов, тегов;
- защищённые роуты через HTTPBearer.

Все SQL-запросы вынесены в отдельный модуль `dal/`.

---

# Supporting Service — Flask 🧩

Вспомогательный сервис. Отвечает за:

| Эндпоинт | Описание |
|---|---|
| `GET /api/v1/supporting/analytics` | Общая статистика системы |
| `GET /api/v1/supporting/dashboard?agent={username}` | Аналитика задач текущего пользователя |
| `GET /api/v1/supporting/hash/<str>` | SHA256 хеширование строки |
| `GET /api/v1/supporting/about` | Данные о проекте из about.json |

Эндпоинты реализованы по требованию ТЗ, на фронте используется только `/dashboard`.

Все SQL-запросы вынесены в отдельный модуль `dal/`.

---

# Модели данных 🗂️

## User
- `username`, `password_hash`

## Task
- `task_number`, `description`, `deadline`, `priority`, `status`, `project_id`, `tag_id`
- статусы: `todo`, `in_progress`, `done`, `on_hold`
- приоритеты: `low`, `medium`, `high`

## Project
- `name`, `user_id`, `created_at`

## Tag
- `name`, `color`, `user_id`, `created_at`

---

# API endpoints 🌐

## FastAPI

```http
POST   /api/register
POST   /api/login
GET    /api/users/{username}
POST   /api/users/{username}/refresh-token
GET    /api/tasks
POST   /api/tasks
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
GET    /api/projects
POST   /api/projects
GET    /api/tags
POST   /api/tags
```

## Flask

```http
GET /api/v1/supporting/analytics
GET /api/v1/supporting/dashboard?agent={username}
GET /api/v1/supporting/hash/<str>
GET /api/v1/supporting/about
```

---

# Стек технологий 🛠️

- **Backend:** Python, FastAPI, Flask
- **Database:** MySQL, чистый SQL (без ORM)
- **Frontend:** Vanilla JS, Bootstrap 5, Chart.js
- **Auth:** JWT, bcrypt
- **Libs:** aiomysql, pymysql, python-dotenv

---

# Как запустить 🚀

## 1. Клонировать репозиторий

```bash
git clone https://github.com/ColonelPavlov/Task_manager
cd Task_manager
```

## 2. Развернуть базу данных

Создать базу данных MySQL и выполнить `script.sql` из корня проекта — он создаст все необходимые таблицы и связи.

## 3. Настроить `.env`

Создать `.env` в папках `Core/` и `Supporting/`:

```env
DB_USER=your_user
DB_PASS=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=your_db
JWT_SECRET_KEY=your_secret
JWT_ALGORITHM=HS256
```

## 4. Установить зависимости и запустить сервисы

Подробная инструкция по настройке виртуальных окружений и запуску обоих сервисов описана в **`DEVELOPMENT-README.md`** в корне проекта.

Краткий вариант:

```bash
# FastAPI (из папки Core/)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Flask (из папки Supporting/)
pip install -r requirements.txt
python main.py
```

## 5. Открыть фронт

Открыть `Frontend/logboot.html` в браузере.

---

# Команда проекта 👨‍💻

| Роль | Никнейм |
|---|---|
| Lead Scrum Master | CapStarCat |
| QA Engineer | Y-M-Are |
| Backend Engineer | an-oxidizer |
| Database Engineer | ColonelPavlov |
| Frontend Engineer | DieVox-Rus |
