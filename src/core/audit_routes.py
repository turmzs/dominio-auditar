from flask import Blueprint, jsonify, request
from src.database.session import get_session
from src.models.audit import SystemLog
from sqlalchemy import func

bp = Blueprint('audit_routes', __name__, url_prefix='/api/logs')

@bp.route('', methods=['GET'])
def get_logs():
    tabela = request.args.get('tabela')
    registro_id = request.args.get('registro_id')
    usuario_id = request.args.get('usuario_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    session = get_session()
    try:
        query = session.query(SystemLog)
        
        if tabela:
            query = query.filter(SystemLog.tabela == tabela)
        if registro_id:
            query = query.filter(SystemLog.registro_id == int(registro_id))
        if usuario_id:
            query = query.filter(SystemLog.usuario_id == int(usuario_id))
            
        # Ordenar por data decrescente
        query = query.order_by(SystemLog.criado_em.desc())
        
        # Paginação
        total = query.count()
        offset = (page - 1) * per_page
        logs = query.offset(offset).limit(per_page).all()
        
        resultado = []
        for log in logs:
            resultado.append({
                'id': log.id,
                'usuario_id': log.usuario_id,
                'tabela': log.tabela,
                'registro_id': log.registro_id,
                'acao': log.acao,
                'valor_anterior': log.valor_anterior,
                'valor_novo': log.valor_novo,
                'criado_em': log.criado_em.isoformat() if log.criado_em else None
            })
            
        return jsonify({
            'logs': resultado,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()

@bp.route('/stats', methods=['GET'])
def get_log_stats():
    session = get_session()
    try:
        # Contagem por acao
        acao_stats = session.query(SystemLog.acao, func.count(SystemLog.id)).group_by(SystemLog.acao).all()
        # Contagem por tabela
        tabela_stats = session.query(SystemLog.tabela, func.count(SystemLog.id)).group_by(SystemLog.tabela).all()
        
        return jsonify({
            'por_acao': {acao: count for acao, count in acao_stats},
            'por_tabela': {tabela: count for tabela, count in tabela_stats}
        }), 200
    except Exception as e:
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        session.close()
