como ja esta "from flask import Blueprint, jsonify

bp = Blueprint('fornecedores', __name__, url_prefix='/fornecedores')

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'fornecedores'}), 200
"