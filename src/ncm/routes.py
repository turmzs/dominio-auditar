"from flask import Blueprint, jsonify

bp = Blueprint('ncm', __name__, url_prefix='/ncm')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'ncm'}), 200
"