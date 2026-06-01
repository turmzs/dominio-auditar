from flask import Blueprint, jsonify

bp = Blueprint("integracoes", __name__, url_prefix="/integracoes")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "integracoes"}), 200
