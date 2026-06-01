from flask import Blueprint, jsonify

bp = Blueprint("obrigacoes", __name__, url_prefix="/obrigacoes")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "obrigacoes_acessorias"}), 200
