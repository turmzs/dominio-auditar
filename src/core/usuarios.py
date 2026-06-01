from flask import Blueprint, jsonify

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'usuarios'}), 200
"