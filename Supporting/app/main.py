from flask import Flask, jsonify
from app.routers.analytics import analytics_bp
from app.routers.hash import hash_bp

app = Flask(__name__)

app.register_blueprint(analytics_bp)
app.register_blueprint(hash_bp)


@app.route("/")
def home_page():
    return jsonify({
        "status": "active",
        "service": "Supporting(Flask)",
        "message": "Система аналитики и шлюза Murkoff Corporation запущена"
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # macOS, отдай 5000