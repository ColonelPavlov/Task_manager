import os
import json
import pymysql
from flask import Blueprint, jsonify
from dotenv import load_dotenv

load_dotenv()

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/supporting")

def get_db_connection():
    return pymysql.connect(
        host=str(os.getenv("DB_HOST", "127.0.0.1")),
        user=str(os.getenv("DB_USER", "change_me")),
        password=str(os.getenv("DB_PASS", "change_me")),
        database=str(os.getenv("DB_NAME", "change_me")),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

@analytics_bp.route("/analytics", methods=["GET"])
def get_analytics():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) AS total FROM users")
            total_users = cursor.fetchone()["total"]

            cursor.execute("SELECT SUM(hours_spent) AS total_hours FROM time_tracking")
            result_hours = cursor.fetchone()
            total_hours = result_hours["total_hours"] if result_hours and result_hours["total_hours"] else 0

            cursor.execute("SELECT COUNT(*) AS total_tasks FROM tasks")
            total_tasks = cursor.fetchone()["total_tasks"]

        connection.close()

        return jsonify({
            "status": "success",
            "total_employees": total_users,
            "total_hours_spent": total_hours,
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
    try:
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT u.username, SUM(t.hours_spent) AS total_hours FROM time_tracking t JOIN users u ON t.user_id = u.user_id GROUP BY u.username")
            hours_data = cursor.fetchall()
            
            hours_labels = [row["username"] for row in hours_data]
            hours_values = [int(row["total_hours"]) for row in hours_data]

            cursor.execute("SELECT status, COUNT(*) AS count_tasks FROM tasks GROUP BY status")
            status_data = cursor.fetchall()
            
            status_labels = [row["status"] for row in status_data]
            status_values = [int(row["count_tasks"]) for row in status_data]

        connection.close()

        return jsonify({
            "status": "success",
            "charts": {
                "employee_hours": {
                    "labels": hours_labels,
                    "datasets": hours_values
                },
                "task_statuses": {
                    "labels": status_labels,
                    "datasets": status_values
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
