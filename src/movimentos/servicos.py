from flask import Blueprint, jsonify

bp = Blueprint("servicos", __name__, url_prefix="/movimentos/servicos")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "movimentos_servicos"}), 200
