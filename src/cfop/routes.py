from flask import Blueprint, jsonify

bp = Blueprint('cfop', __name__, url_prefix='/cfop')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'cfop'}), 200
