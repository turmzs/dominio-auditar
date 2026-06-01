from flask import Blueprint, jsonify

bp = Blueprint("sped", __name__, url_prefix="/obrigacoes/sped")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "obrigacoes_sped"}), 200
