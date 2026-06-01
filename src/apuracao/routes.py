from flask import Blueprint, jsonify

bp = Blueprint("apuracao", __name__, url_prefix="/apuracao")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "apuracao"}), 200
