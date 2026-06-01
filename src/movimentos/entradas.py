from flask import Blueprint, jsonify

bp = Blueprint("entradas", __name__, url_prefix="/movimentos/entradas")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "movimentos_entradas"}), 200
