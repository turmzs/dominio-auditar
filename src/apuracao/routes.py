from flask import Blueprint, jsonify, request
from src.apuracao.engine import ApuracaoEngine
from src.models.apuracao import Apuracao
from src.database.session import get_session

bp = Blueprint('apuracao', __name__, url_prefix='/apuracao')

@bp.route('/calcular', methods=['POST'])
def calcular_apuracao():
    try:
        data = request.json
        company_id = data.get('empresa_id')
        mes = data.get('mes')
        ano = data.get('ano')
        imposto = (data.get('imposto') or 'ICMS').upper()

        if imposto in ['PRESUMIDO', 'REAL']:
            imposto = 'ICMS'

        if not all([company_id, mes, ano]):

            return jsonify({'status': 'erro', 'message': 'Parametros empresa_id, mes e ano sao obrigatorios'}), 400

        engine = ApuracaoEngine(company_id=int(company_id))

        # Buscar regime_tributario com consulta direta e robusta
        session = get_session()
        try:
            # import direto evita problemas de namespace/dynamic import
            from src.models.base import Company
            company = session.query(Company).filter(Company.id == int(company_id)).first()
        except Exception:
            company = None
        finally:
            session.close()

        # Se a empresa não existir, retorna para a UI com diagnóstico
        if company is None:
            return jsonify({
                'status': 'erro',
                'message': 'Empresa não encontrada para este company_id',
                'received_company_id': company_id
            }), 404


        # Segurança extra: normaliza imposto
        # Enquanto o engine de apuração por regime não está integrado totalmente,
        # o backend atual suporta:
        # - ICMS (calcular_icms)
        # - PIS/COFINS (calcular_pis_cofins)
        # - SIMPLES (calcular_simples)
        if imposto == 'ICMS':
            resultado = engine.calcular_icms(int(mes), int(ano))
        elif imposto in ['PIS', 'COFINS']:
            resultado = engine.calcular_pis_cofins(int(mes), int(ano), imposto=imposto)
        elif imposto == 'SIMPLES':
            resultado = engine.calcular_simples(int(mes), int(ano))
        else:
            # PRESUMIDO/REAL chegam como ICMS (mapeado acima). Se chegar aqui, fallback para ICMS.
            resultado = engine.calcular_icms(int(mes), int(ano))


        return jsonify({
            'status': 'sucesso',
            'apuracao_id': resultado.id,
            'total_debito': float(resultado.valor_total_debito or 0),
            'total_credito': float(resultado.valor_total_credito or 0),
            'valor_final': float(resultado.valor_final or 0),
            'status_apuracao': resultado.status
        }), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500

@bp.route('/resumo', methods=['GET'])
def get_resumo():
    try:
        company_id = request.args.get('empresa_id')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        imposto = (request.args.get('imposto') or 'ICMS').upper()

        if imposto in ['PRESUMIDO', 'REAL']:
            imposto = 'ICMS'

        session = get_session()

        apuracao = session.query(Apuracao).filter(
            Apuracao.empresa_id == company_id,
            Apuracao.mes == mes,
            Apuracao.ano == ano,
            Apuracao.imposto == imposto
        ).first()

        if not apuracao:
            return jsonify({'status': 'erro', 'message': 'Apuracao nao encontrada para este periodo'}), 404

        return jsonify({
            'id': apuracao.id,
            'imposto': apuracao.imposto,
            'periodo': f'{apuracao.mes}/{apuracao.ano}',
            'debito': float(apuracao.valor_total_debito),
            'credito': float(apuracao.valor_total_credito),
            'final': float(apuracao.valor_final),
            'status': apuracao.status
        }), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500
