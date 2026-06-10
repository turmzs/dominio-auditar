from flask import Blueprint, jsonify, request
from src.database.session import get_session
from src.models.fiscal import FiscalMovement
from src.models.audit import AuditAlert
from motor_fiscal.engine.executor import FiscalExecutor
from datetime import date
import calendar

bp = Blueprint('auditorias_api', __name__, url_prefix='/api/auditoria')

@bp.route('/executar', methods=['GET', 'POST'])
def executar_auditoria():
    empresa_id = request.args.get('empresa_id') or request.form.get('empresa_id')
    mes = request.args.get('mes') or request.form.get('mes')
    ano = request.args.get('ano') or request.form.get('ano')
    
    if not empresa_id or not mes or not ano:
        return jsonify({'status': 'erro', 'message': 'empresa_id, mes e ano sao obrigatorios'}), 400
        
    session = get_session()
    try:
        empresa_id = int(empresa_id)
        mes = int(mes)
        ano = int(ano)
        
        start_date = date(ano, mes, 1)
        _, last_day = calendar.monthrange(ano, mes)
        end_date = date(ano, mes, last_day)
        
        movements = session.query(FiscalMovement).filter(
            FiscalMovement.empresa_id == empresa_id,
            FiscalMovement.data_emissao >= start_date,
            FiscalMovement.data_emissao <= end_date
        ).all()
        
        executor = FiscalExecutor()
        total_movimentos = len(movements)
        total_alertas = 0
        
        for mov in movements:
            alertas_mov = executor.processar_movimento(mov.id)
            total_alertas += alertas_mov
            
        return jsonify({
            'status': 'sucesso',
            'movimentos_processados': total_movimentos,
            'total_alertas_gerados': total_alertas
        }), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()

@bp.route('/alertas', methods=['GET'])
def listar_alertas():
    empresa_id = request.args.get('empresa_id')
    mes = request.args.get('mes')
    ano = request.args.get('ano')
    
    if not empresa_id:
        return jsonify({'status': 'erro', 'message': 'empresa_id eh obrigatorio'}), 400
        
    session = get_session()
    try:
        empresa_id = int(empresa_id)
        query = session.query(AuditAlert).filter(AuditAlert.empresa_id == empresa_id)
        
        if mes and ano:
            mes = int(mes)
            ano = int(ano)
            start_date = date(ano, mes, 1)
            _, last_day = calendar.monthrange(ano, mes)
            end_date = date(ano, mes, last_day)
            
            query = query.join(FiscalMovement, AuditAlert.movimento_id == FiscalMovement.id).filter(
                FiscalMovement.data_emissao >= start_date,
                FiscalMovement.data_emissao <= end_date
            )
            
        alertas = query.all()
        resultado = []
        for a in alertas:
            resultado.append({
                'id': a.id,
                'movimento_id': a.movimento_id,
                'item_id': getattr(a, 'item_id', None),
                'regra_id': getattr(a, 'regra_id', ''),
                'tipo': a.tipo,
                'severidade': a.severidade,
                'descricao': a.descricao,
                'resolvido': a.resolvido,
                'criado_em': a.criado_em.isoformat() if a.criado_em else None
            })
            
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()

@bp.route('/resolver/<int:alert_id>', methods=['POST'])
def resolver_alerta(alert_id):
    session = get_session()
    try:
        alerta = session.query(AuditAlert).filter(AuditAlert.id == alert_id).first()
        if not alerta:
            return jsonify({'status': 'erro', 'message': 'Alerta nao encontrado'}), 404
            
        alerta.resolvido = True
        session.commit()
        return jsonify({'status': 'sucesso', 'message': f'Alerta {alert_id} marcado como resolvido'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()

@bp.route('/resumo', methods=['GET'])
def resumo_alertas():
    empresa_id = request.args.get('empresa_id')
    if not empresa_id:
        return jsonify({'status': 'erro', 'message': 'empresa_id eh obrigatorio'}), 400
        
    session = get_session()
    try:
        empresa_id = int(empresa_id)
        alertas = session.query(AuditAlert).filter(AuditAlert.empresa_id == empresa_id, AuditAlert.resolvido == False).all()
        
        resumo = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'total': 0
        }
        
        for a in alertas:
            sev = (a.severidade or 'warning').lower()
            if sev in resumo:
                resumo[sev] += 1
            else:
                resumo['warning'] += 1
            resumo['total'] += 1
            
        return jsonify(resumo), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()
