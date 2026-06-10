from flask import Blueprint, jsonify, request, render_template

from src.database.session import get_session

from src.models.fiscal import FiscalMovement, FiscalMovementItem
from src.models.audit import MotorFiscalResultado, AuditAlert

bp = Blueprint("motor_fiscal", __name__, url_prefix="/motor_fiscal")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "motor_fiscal"}), 200


@bp.route("/audit_results", methods=["GET"])
def audit_results_page():
    return render_template("audit_results.html")


@bp.route("/resultado/<int:movimento_id>", methods=["GET"])
def resultado_page(movimento_id: int):
    """Retorna JSON no formato esperado por templates/audit_results.html."""

    session = get_session()
    try:
        movimento = (
            session.query(FiscalMovement)
            .filter(FiscalMovement.id == movimento_id)
            .first()
        )
        if not movimento:
            return jsonify({"status": "erro", "message": "Movimento nao encontrado", "itens": []}), 404

        itens = (
            session.query(FiscalMovementItem)
            .filter(FiscalMovementItem.movimento_id == movimento_id)
            .all()
        )

        if itens and not session.query(MotorFiscalResultado).join(
            FiscalMovementItem,
            MotorFiscalResultado.item_movimento_id == FiscalMovementItem.id,
        ).filter(FiscalMovementItem.movimento_id == movimento_id).first():
            from motor_fiscal.engine.executor import FiscalExecutor
            FiscalExecutor().processar_movimento(movimento_id)

        alertas_mov = (
            session.query(AuditAlert)
            .filter(AuditAlert.movimento_id == movimento_id, AuditAlert.resolvido == False)
            .all()
        )
        alertas_por_item = {}
        for alerta in alertas_mov:
            item_ref = getattr(alerta, "item_id", None)
            alertas_por_item.setdefault(item_ref, []).append(alerta)

        tipo_doc = (getattr(movimento, 'tipo_documento', None) or 'NFE').upper()
        is_nfse = tipo_doc == 'NFSE'

        payload = []
        for it in itens:
            res = (
                session.query(MotorFiscalResultado)
                .filter(MotorFiscalResultado.item_movimento_id == it.id)
                .first()
            )

            gera_debito = bool(getattr(res, "gera_debito", False)) if res else False
            gera_credito = bool(getattr(res, "gera_credito", False)) if res else False
            monofasico = bool(getattr(res, "monofasico", False)) if res else False
            st = bool(getattr(res, "substituicao_tributaria", False)) if res else False
            motivo = getattr(res, "motivo", None) if res else None

            alertas = []
            for alerta in alertas_por_item.get(it.id, []):
                desc = (alerta.descricao or "").strip()
                if not desc:
                    continue

                tipo = (getattr(alerta, "tipo", None) or "Geral").strip()
                severidade = getattr(alerta, "severidade", None) or "warning"

                # Hint simples por tipo (heurística inicial)
                hint = None
                tipo_norm = tipo.upper()
                if "NCM" in tipo_norm:
                    hint = "Verifique o NCM no XML e/ou no cadastro do produto. Se for serviço (NFSE), garanta que o mapeamento esteja correto."
                elif "CFOP" in tipo_norm:
                    hint = "Verifique o CFOP do item no XML e o padrão do tipo de operação (entrada/saída). Ajuste o CFOP no movimento ou no cadastro quando aplicável."
                elif "CST" in tipo_norm or "CSOSN" in tipo_norm:
                    hint = "Conferir CST/CSOSN para o cenário tributário (regime e operação). Corrija o campo no item (ou garanta que o parser preenche corretamente)."
                elif "MONOF" in tipo_norm or "MONOFÁSICO" in tipo_norm:
                    hint = "Itens monofásicos exigem regra específica. Confirme se o produto é monofásico e se o CST/CSOSN estão compatíveis."
                elif "CREDITO" in tipo_norm:
                    hint = "Verifique a existência e elegibilidade do crédito (base, CST, NCM/CFOP e regras do regime). Corrija o item/cadastros antes de reprocessar."
                else:
                    # fallback
                    hint = "Analise a descrição do alerta e ajuste o item/cadastros relacionados. Depois reprocessar o movimento."

                alertas.append(
                    {
                        "tipo": tipo,
                        "severidade": severidade,
                        "descricao": desc,
                        "hint": hint,
                    }
                )

            dec = "CONFLITO" if alertas else "OK"

            codigo_servico = it.ncm if is_nfse else None
            iss_valor = float(it.valor_pis or 0) if is_nfse else 0

            valor_item = float(it.valor_total or 0)

            payload.append(
                {
                    "produto": it.descricao,
                    "ncm": None if is_nfse else it.ncm,
                    "codigo_servico": codigo_servico,
                    "valor_total": valor_item,
                    "cst": (
                        f"ISS R$ {iss_valor:.2f}" if is_nfse
                        else (it.cst_icms or getattr(it, "csosn", "") or "-")
                    ),
                    "decisao": dec,
                    "st": "SIM" if st else "NÃO",
                    "credito": "SIM" if gera_credito else "NÃO",
                    "debito": "SIM" if gera_debito else "NÃO",
                    "monofasico": "SIM" if monofasico else "NÃO",
                    "alertas": alertas,
                }
            )

        hint = None
        if not payload:
            hint = (
                "Este movimento nao possui itens. Pode ser NFS-e, XML incompleto "
                "ou importacao anterior a correcao do parser."
            )

        soma_itens = sum(p.get("valor_total", 0) for p in payload)
        valor_nota = float(movimento.valor_total or 0) or soma_itens

        return jsonify({
            "status": "sucesso",
            "movimento_id": movimento_id,
            "numero_nota": movimento.numero_nota,
            "tipo_documento": getattr(movimento, "tipo_documento", None),
            "valor_total": valor_nota,
            "soma_itens": soma_itens,
            "valor_icms": float(movimento.valor_icms or 0),
            "valor_pis": float(movimento.valor_pis or 0),
            "valor_cofins": float(movimento.valor_cofins or 0),
            "total_itens": len(payload),
            "total_alertas": sum(1 for p in payload if p.get("alertas")),
            "hint": hint,
            "itens": payload,
        })
    finally:
        session.close()

