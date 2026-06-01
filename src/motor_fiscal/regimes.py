from flask import Blueprint, jsonify

bp = Blueprint("regimes", __name__, url_prefix="/motor_fiscal/regimes")


@bp.route("/simples", methods=["GET"])
def simples():
    return jsonify({"regime": "Simples Nacional", "status": "placeholder"}), 200


@bp.route("/presumido", methods=["GET"])
def presumido():
    return jsonify({"regime": "Lucro Presumido", "status": "placeholder"}), 200


@bp.route("/real", methods=["GET"])
def real():
    return jsonify({"regime": "Lucro Real", "status": "placeholder"}), 200
