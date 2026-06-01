from flask import Blueprint, jsonify

bp = Blueprint("guias", __name__, url_prefix="/apuracao/guias")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "apuracao_guias"}), 200
