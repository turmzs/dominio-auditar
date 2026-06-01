"from flask import Blueprint, jsonify

bp = Blueprint('permissoes', __name__, url_prefix='/permissoes')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'permissoes'}), 200
"