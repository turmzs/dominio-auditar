from flask import Blueprint, jsonify

bp = Blueprint("ajuda", __name__, url_prefix="/ajuda")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "ajuda"}), 200
