import hashlib
from flask import Blueprint, jsonify

hash_bp = Blueprint("hash", __name__, url_prefix="/api/v1/supporting")


# Однажды я пойму почему этот роут был в тз. Однажды, но не сейчас...

@hash_bp.route("/hash/<string:user_str>", methods=["GET"])
def get_string_hash(user_str):
    hashed_result = hashlib.sha256(user_str.encode('utf-8')).hexdigest()
    return jsonify({
        "request": user_str,
        "result": hashed_result
    })
