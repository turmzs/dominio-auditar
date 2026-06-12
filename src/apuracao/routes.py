from flask import Blueprint, jsonify, request
from src.apuracao.engine import ApuracaoEngine
from src.models.apuracao import Apuracao
from src.database.session import get_session

bp = Blueprint('apuracao', __name__, url_prefix='/apuracao')

@bp.route('/calcular', methods=['POST'])
def calcular_apuracao():
    session = None
    engine = None
    try:
        data = request.json or {}
        company_id = data.get('empresa_id')
        mes = data.get('mes')
        ano = data.get('ano')
        imposto = (data.get('imposto') or 'ICMS').upper()

        if imposto in ['PRESUMIDO', 'REAL']:
            imposto = 'ICMS'

        if not all([company_id, mes, ano]):
            return jsonify({'status': 'erro', 'message': 'Parametros empresa_id, mes e ano sao obrigatorios'}), 400

        # Validar empresa antes de rodar engine
        session = get_session()
        from src.models.base import Company
        company = session.query(Company).filter(Company.id == int(company_id)).first()
        if company is None:
            return jsonify({
                'status': 'erro',
                'message': 'Empresa não encontrada para este company_id',
                'received_company_id': company_id
            }), 404

        engine = ApuracaoEngine(company_id=int(company_id))

        if imposto == 'ICMS':
            resultado = engine.calcular_icms(int(mes), int(ano))
        elif imposto in ['PIS', 'COFINS']:
            resultado = engine.calcular_pis_cofins(int(mes), int(ano), imposto=imposto)
        elif imposto == 'SIMPLES':
            resultado = engine.calcular_simples(int(mes), int(ano))
        else:
            resultado = engine.calcular_icms(int(mes), int(ano))

        return jsonify({
            'status': 'sucesso',
            'apuracao_id': resultado.id,
            'total_debito': float(getattr(resultado, 'total_debitos', 0) or 0),
            'total_credito': float(getattr(resultado, 'total_creditos', 0) or 0),
            'valor_final': float(getattr(resultado, 'saldo', 0) or 0),
        }), 200
    except Exception as e:
        # evita manter transação aberta em caso de erro
        try:
            if session is not None:
                session.rollback()
        except Exception:
            pass

        # Debug: mostra o que a engine está vendo no sqlite_master
        sqlite_tables = []
        db_hint = None
        try:
            if engine is not None:
                bind = engine.session.get_bind()
                # tenta obter lista de tabelas
                try:
                    conn = bind.connect()
                    cur = conn.connection.cursor()
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    sqlite_tables = [r[0] for r in cur.fetchall()]
                    conn.close()
                except Exception:
                    sqlite_tables = []

                # hint do banco (quando possível)
                try:
                    db_hint = getattr(bind, "database", None)
                    if db_hint is None:
                        db_hint = getattr(getattr(bind, "url", None), "database", None)
                except Exception:
                    db_hint = None
        except Exception:
            sqlite_tables = []

# debug adicional: tenta extrair URL do sqlite (arquivo)
        debug_bind_url = None
        try:
            if engine is not None:
                bind = engine.session.get_bind()
                debug_bind_url = str(getattr(getattr(bind, "engine", None), "url", None) or getattr(bind, "url", None) or "")
        except Exception:
            debug_bind_url = None

        # debug tabelas sem filtro (se possível)
        sqlite_all = []
        try:
            if engine is not None:
                bind = engine.session.get_bind()
                conn = bind.connect()
                cur = conn.connection.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                sqlite_all = [r[0] for r in cur.fetchall()]
                conn.close()
        except Exception:
            sqlite_all = sqlite_tables or []

# debug: mostra qual DATABASE_URL o backend está usando (evita confusão de DB relativo)
        debug_database_url = None
        debug_database_file_exists = None
        debug_database_file_size = None
        try:
            import os
            from src.database.session import DATABASE_URL as _DATABASE_URL

            debug_database_url = _DATABASE_URL
            if _DATABASE_URL.startswith("sqlite:///"):
                db_file = _DATABASE_URL.replace("sqlite:///", "", 1)
                debug_database_file_exists = os.path.exists(db_file)
                debug_database_file_size = os.path.getsize(db_file) if debug_database_file_exists else None
        except Exception:
            pass

        return jsonify(
            {
                'status': 'erro',
                'message': str(e),
                'debug_db': str(db_hint),
                'debug_bind_url': debug_bind_url,
                'debug_database_url': debug_database_url,
                'debug_database_file_exists': debug_database_file_exists,
                'debug_database_file_size_bytes': debug_database_file_size,
                'debug_sqlite_master_tables': sqlite_tables,
                'debug_sqlite_master_tables_all': sqlite_all,
            }
        ), 500
    finally:
        try:
            if session is not None:
                session.close()
        except Exception:
            pass


@bp.route('/resumo', methods=['GET'])
def get_resumo():
    session = None
    try:
        company_id = request.args.get('empresa_id')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        imposto = (request.args.get('imposto') or 'ICMS').upper()

        if imposto in ['PRESUMIDO', 'REAL']:
            imposto = 'ICMS'

        if not all([company_id, mes, ano]):
            return jsonify({'status': 'erro', 'message': 'Parametros empresa_id, mes e ano sao obrigatorios'}), 400

        session = get_session()
        competencia = f"{int(ano)}-{int(mes):02d}"

        apuracao = session.query(Apuracao).filter(
            Apuracao.empresa_id == company_id,
            Apuracao.competencia == competencia,
            Apuracao.tipo_imposto == imposto
        ).first()

        if not apuracao:
            return jsonify({'status': 'erro', 'message': 'Apuracao nao encontrada para este periodo'}), 404

        return jsonify({
            'id': apuracao.id,
            'imposto': apuracao.tipo_imposto,
            'periodo': apuracao.competencia,
            'debito': float(getattr(apuracao, 'total_debitos', 0) or 0),
            'credito': float(getattr(apuracao, 'total_creditos', 0) or 0),
            'final': float(getattr(apuracao, 'saldo', 0) or 0),
        }), 200
    except Exception as e:
        try:
            if session is not None:
                session.rollback()
        except Exception:
            pass
        return jsonify({'status': 'erro', 'message': str(e)}), 500
    finally:
        try:
            if session is not None:
                session.close()
        except Exception:
            pass
