from flask import Flask, jsonify
import json
import hashlib

app = Flask(__name__)

@app.route("/")
def home_page():
    return jsonify({
        "status": "active",
        "service": "Supporting(Flask)",
        "message": "Система аналитики и шлюза Murkoff Corporation запущена"
    })

@app.route("/api/v1/supporting/analytics", methods=["GET"])
def get_analytics():
    # TODO: for [Backend(Я)] В будущем здесь будет сбор данных из базы данных
    # Сколько сотрудников онлайн, сколько задач выполнено и всякие штучки в json формате.
    return jsonify({
        "total_employees": 5,  # Где помощь?!
        "active_experiments": 2,  # Сервиса потому что два
        "system_status": "SECURE",  # А как иначе?
        "security_breaches_detected": 0  # DevSecOps в чате?
    })

@app.route('/api/v1/supporting/about', methods=['GET'])
def get_about_info():
    try:
        with open('about.json', 'r', encoding='utf-8') as file:
            about_data = json.load(file)
        return jsonify(about_data)
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "Файл конфигурации о проекте не найден на сервере Murkoff."
        }), 404

# Однажды я пойму почему этот роут был в тз. Однажды, но не сейчас...

@app.route('/api/v1/supporting/hash/<string:user_str>', methods=['GET'])
def get_string_hash(user_str):
    hashed_result = hashlib.sha256(user_str.encode('utf-8')).hexdigest()
    return jsonify({
        "request": user_str,
        "result": hashed_result
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # macOS, отдай 5000