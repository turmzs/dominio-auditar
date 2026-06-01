from flask import Blueprint, jsonify

bp = Blueprint("saidas", __name__, url_prefix="/movimentos/saidas")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "movimentos_saidas"}), 200
