from __future__ import annotations

from flask import Blueprint, jsonify, request

from database import DatabaseManager
from .competence_api import calculate_competence_events

bp = Blueprint("domain_competence", __name__, url_prefix="/api/domain")

db = DatabaseManager()



@bp.route("/competence/summary", methods=["GET"])
def competence_summary():
    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)

        if not all([empresa_id, mes, ano]):
            return jsonify({"error": "empresa_id, mes, ano são obrigatórios"}), 400

        assert empresa_id is not None and mes is not None and ano is not None
        result = calculate_competence_events(db=db, empresa_id=empresa_id, mes=mes, ano=ano)

        event = result["event"]

        # retorno reduzido pra facilitar debug
        return jsonify(
            {
                "event_key": event.event_key,
                "numero": event.numero,
                "regime": event.operacao.regime,
                "activity_type": event.operacao.activity_type,
                "taxes": [t.__dict__ for t in event.taxes],
                "inconsistencies": event.inconsistencies,
                "debug": event.debug,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

