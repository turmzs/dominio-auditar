from flask import Blueprint, jsonify

bp = Blueprint("nfse", __name__, url_prefix="/xml/nfse")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "xml_nfse"}), 200
