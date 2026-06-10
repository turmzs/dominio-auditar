from __future__ import annotations

from flask import Blueprint, jsonify, request

from database import DatabaseManager
from src.domain_canonic.competence_api import calculate_competence_events



bp_output = Blueprint("obrigacoes_output", __name__, url_prefix="/obrigacoes/output")

db = DatabaseManager()


@bp_output.route("/competence", methods=["GET"])
def output_competence_summary():
    """Output mínimo (fase 2): expõe um resumo canônico para consumo de camadas de conferência.

    Observação: nesta fase ainda é placeholder, pois os impostos ainda não estão distribuídos
    por item/nota (ver etapa 1/5).
    """

    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)

        if not all([empresa_id, mes, ano]):
            return jsonify({"error": "empresa_id, mes, ano são obrigatórios"}), 400

        # Como validamos com `if not all([empresa_id, mes, ano])`, aqui tratamos como não-None.
        result = calculate_competence_events(  # type: ignore[arg-type]
            db=db, empresa_id=int(empresa_id), mes=int(mes), ano=int(ano)
        )



        event = result["event"]

        return jsonify(
            {
                "event_key": event.event_key,
                "numero": event.numero,
                "regime": event.operacao.regime,
                "activity_type": event.operacao.activity_type,
                "totals": {
                    "total": event.amounts.total,
                    "pis": event.amounts.pis,
                    "cofins": event.amounts.cofins,
                    "icms": event.amounts.icms,
                    "iss": event.amounts.iss,
                },
                "taxes": [t.__dict__ for t in event.taxes],
                "inconsistencies": event.inconsistencies,
                "debug": event.debug,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

