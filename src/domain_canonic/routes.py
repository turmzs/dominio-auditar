from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from database import DatabaseManager
from .adapter import build_canonical_event_from_parsed

bp = Blueprint("domain_canonic", __name__, url_prefix="/api/domain")

db = DatabaseManager()


@bp.route("/test/transform", methods=["POST"])
def transform_test():
    """Endpoint de teste: transforma o payload atual do parser em CanonicalFiscalEvent."""
    data = request.json or {}
    empresa_id = data.get("empresa_id")
    parsed = data.get("parsed")

    if not empresa_id or not parsed:
        return jsonify({"error": "empresa_id e parsed são obrigatórios"}), 400

    empresa = db.obter_empresa(int(empresa_id))
    if not empresa:
        return jsonify({"error": "Empresa não encontrada"}), 404

    event = build_canonical_event_from_parsed(
        company_id=int(empresa_id),
        nota_id=parsed.get("id"),
        parsed=parsed,
        regime=empresa.get("regime"),
        activity_type=empresa.get("atividade"),
        xml_origem=str(parsed.get("xml_origem") or ""),
    )

    return jsonify({"event_key": event.event_key, "taxes": event.taxes, "inconsistencies": event.inconsistencies, "debug": event.debug})

