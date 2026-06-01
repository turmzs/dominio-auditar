# src/core/login.py
from flask import Blueprint, jsonify, request

bp = Blueprint("login", __name__, url_prefix="/login")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "login"}), 200
