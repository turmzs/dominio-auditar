"from flask import Blueprint, jsonify

bp = Blueprint('produtos', __name__, url_prefix='/produtos')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'produtos'}), 200
"