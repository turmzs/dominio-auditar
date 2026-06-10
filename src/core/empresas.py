from flask import Blueprint, jsonify, request

from src.database.session import get_session
from src.models.base import Company

bp = Blueprint('empresas', __name__, url_prefix='/empresas')


@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'module': 'empresas'}), 200


@bp.route('/api/empresas', methods=['GET'])
def listar_empresas():
    session = get_session()
    try:
        empresas = session.query(Company).filter(Company.ativo == True).order_by(Company.id.asc()).all()
        return jsonify([
            {
                'id': e.id,
                'cnpj': e.cnpj,
                'nome': e.nome_fantasia or e.razao_social,
                'razao_social': e.razao_social,
                'regime_tributario': e.regime_tributario,
                'uf': e.uf,
                'municipio': e.municipio,
            }
            for e in empresas
        ]), 200
    finally:
        session.close()


@bp.route('/api/empresas', methods=['POST'])
def criar_empresa():
    data = request.json or {}

    nome_fantasia = (data.get('nome_fantasia') or '').strip() or None
    razao_social = (data.get('razao_social') or '').strip()
    cnpj = (data.get('cnpj') or '').strip()
    regime_tributario = (data.get('regime_tributario') or data.get('regime') or '').strip() or None
    uf = (data.get('uf') or '').strip() or None
    municipio = (data.get('municipio') or '').strip() or None

    if not razao_social:
        return jsonify({'status': 'erro', 'message': 'razao_social é obrigatório'}), 400
    if not cnpj:
        return jsonify({'status': 'erro', 'message': 'cnpj é obrigatório'}), 400

    session = get_session()
    try:
        existente = session.query(Company).filter(Company.cnpj == cnpj).first()
        if existente:
            return jsonify({'status': 'erro', 'message': 'Já existe empresa com este CNPJ', 'id': existente.id}), 409

        empresa = Company(
            cnpj=cnpj,
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            regime_tributario=regime_tributario,
            uf=uf,
            municipio=municipio,
            ativo=True,
        )
        session.add(empresa)
        session.commit()
        session.refresh(empresa)

        return jsonify({
            'status': 'sucesso',
            'id': empresa.id,
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()

