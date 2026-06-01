from flask import Blueprint, jsonify

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "relatorios"}), 200
