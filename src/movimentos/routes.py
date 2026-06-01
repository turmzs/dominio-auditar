from flask import Blueprint, jsonify

bp = Blueprint("movimentos", __name__, url_prefix="/movimentos")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "movimentos"}), 200
