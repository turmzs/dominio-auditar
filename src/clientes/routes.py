"from flask import Blueprint, jsonify

bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'clientes'}), 200
"