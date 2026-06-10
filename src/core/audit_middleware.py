from flask import request, session as flask_session
from src.database.session import get_session
from src.models.audit import SystemLog
import json

def audit_log(user_id, tabela, registro_id, acao, valor_anterior=None, valor_novo=None):
    """Grava uma entrada no log de auditoria no banco de dados"""
    session = get_session()
    try:
        # Convert dicts or lists to JSON-serializable structures if needed
        # depending on how SystemLog is set up (usually SQLAlchemy handles JSON/Text columns)
        log = SystemLog(
            usuario_id=user_id,
            tabela=tabela,
            registro_id=registro_id,
            acao=acao,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo
        )
        session.add(log)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Erro ao registrar log de auditoria: {e}")
    finally:
        session.close()

def init_audit_middleware(app):
    @app.after_request
    def log_write_operations(response):
        # Somente loga operacoes de modificacao bem-sucedidas
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH'] and response.status_code < 400:
            # Ignora rotas de login/logout/arquivos estaticos para nao poluir o log
            if any(path in request.path for path in ['/login', '/logout', '/static']):
                return response

            user_id = flask_session.get('user_id')
            if not user_id:
                # Tenta obter usuario da sessao ou usa ID padrao do administrador/sistema
                user_id = 1

            path = request.path
            parts = [p for p in path.split('/') if p]
            
            tabela = 'requisicao'
            registro_id = None
            
            if parts:
                tabela = parts[-1]
                if tabela.isdigit():
                    registro_id = int(tabela)
                    if len(parts) >= 2:
                        tabela = parts[-2]
            
            # Captura corpo da requisicao (novos valores)
            valor_novo = None
            try:
                if request.is_json:
                    valor_novo = request.get_json(silent=True)
                else:
                    valor_novo = dict(request.form)
                    # Remove senhas/chaves secretas por seguranca
                    if 'senha' in valor_novo:
                        valor_novo['senha'] = '******'
                    if 'password' in valor_novo:
                        valor_novo['password'] = '******'
            except Exception:
                pass

            audit_log(
                user_id=user_id,
                tabela=tabela,
                registro_id=registro_id,
                acao=request.method,
                valor_anterior=None,
                valor_novo=valor_novo
            )
            
        return response
