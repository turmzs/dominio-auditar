"from flask import Blueprint, jsonify

bp = Blueprint('empresas', __name__, url_prefix='/empresas')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'empresas'}), 200
"