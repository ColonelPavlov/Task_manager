import os
import json
import pymysql
from flask import Blueprint, jsonify, request
from app.dal.analytics import get_total_users, get_total_tasks, get_task_priorities_by_user, get_task_statuses_by_user
from dotenv import load_dotenv

load_dotenv()

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/supporting")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "change_me"),
        password=os.getenv("DB_PASS", "change_me"),
        database=os.getenv("DB_NAME", "change_me"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

@analytics_bp.route("/analytics", methods=["GET"])
def get_analytics():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:

            total_users = get_total_users(cursor)
            total_tasks = get_total_tasks(cursor)
            total_tasks = cursor.fetchone()["total_tasks"]

        connection.close()

        return jsonify({
            "status": "success",
            "total_employees": total_users,
            "total_tasks_created": total_tasks,
            "system_status": "SECURE",
            "security_breaches_detected": 0
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

@analytics_bp.route("/dashboard", methods=["GET"])
def get_dashboard_data():
    agent = request.args.get("agent")
    if not agent:
        return jsonify({
            "status": "error",
            "message": "Не передан agent"
        }), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            priority_data = get_task_priorities_by_user(cursor, agent)
            status_data = get_task_statuses_by_user(cursor, agent)

        connection.close()

        return jsonify({
            "status": "success",
            "charts": {
                "task_priorities": {
                    "labels": [row["priority"] for row in priority_data],
                    "datasets": [int(row["count_tasks"]) for row in priority_data]
                },
                "task_statuses": {
                    "labels": [row["status"] for row in status_data],
                    "datasets": [int(row["count_tasks"]) for row in status_data]
                }
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Ошибка сбора данных для дашборда: {str(e)}"
        }), 500

@analytics_bp.route("/about", methods=["GET"])
def get_about_info():
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(base_dir, "about.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            about_data = json.load(file)
        return jsonify(about_data)
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "Файл конфигурации о проекте не найден на сервере Murkoff."
        }), 404
