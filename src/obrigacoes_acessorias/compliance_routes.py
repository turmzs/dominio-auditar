from __future__ import annotations

from flask import Blueprint, jsonify, request

from database import DatabaseManager

bp_compliance = Blueprint("obrigacoes_compliance", __name__, url_prefix="/obrigacoes/compliance")

db = DatabaseManager()


@bp_compliance.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "obrigacoes_acessorias/compliance"}), 200


@bp_compliance.route("/check", methods=["POST"])
def compliance_check():
    """Compliance check placeholder (fase 2).

    Entrada esperada (placeholder):
    {
      "empresa_id": int,
      "mes": int,
      "ano": int,
      "event_key": str (opcional)
    }

    Nesta fase, apenas valida dados e retorna um status.
    """

    try:
        data = request.json or {}
        empresa_id = data.get("empresa_id")
        mes = data.get("mes")
        ano = data.get("ano")

        if not all([empresa_id, mes, ano]):
            return jsonify({"error": "empresa_id, mes, ano são obrigatórios"}), 400

        # Placeholder: aqui entraria validação de aderência a SPED/EFD etc.
        return jsonify(
            {
                "success": True,
                "empresa_id": empresa_id,
                "mes": mes,
                "ano": ano,
                "status": "placeholder_sem_regras_de_validacao_nesta_fase",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

