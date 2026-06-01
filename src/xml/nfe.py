from flask import Blueprint, jsonify

bp = Blueprint("nfe", __name__, url_prefix="/xml/nfe")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "xml_nfe"}), 200
