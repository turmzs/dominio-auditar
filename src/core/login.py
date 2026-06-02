# src/core/login.py
from flask import Blueprint, jsonify, request

bp = Blueprint("login", __name__, url_prefix="/login")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "login"}), 200
from flask import Blueprint, jsonify

bp = Blueprint('ncm', __name__, url_prefix='/ncm')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'ncm'}), 200
