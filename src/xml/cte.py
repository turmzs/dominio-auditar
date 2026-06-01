from flask import Blueprint, jsonify

bp = Blueprint("cte", __name__, url_prefix="/xml/cte")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "xml_cte"}), 200
