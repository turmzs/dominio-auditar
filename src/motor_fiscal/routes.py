from flask import Blueprint, jsonify

bp = Blueprint("motor_fiscal", __name__, url_prefix="/motor_fiscal")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "motor_fiscal"}), 200
