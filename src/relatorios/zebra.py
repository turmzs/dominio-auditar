from flask import Blueprint, jsonify

bp = Blueprint("zebra", __name__, url_prefix="/relatorios/zebra")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "relatorios_zebra"}), 200
