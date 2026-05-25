import os
import json
from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/supporting")

@analytics_bp.route("/analytics", methods=["GET"])
def get_analytics():
    # TODO: for [Backend(Я)] В будущем здесь будет сбор данных из базы данных
    # Сколько сотрудников онлайн, сколько задач выполнено и всякие штучки в json формате.
    return jsonify({
        "total_employees": 5,  # Где помощь?!
        "active_experiments": 2,  # Сервиса потому что два
        "system_status": "SECURE",  # А как иначе?
        "security_breaches_detected": 0  # DevSecOps в чате?
    })

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
