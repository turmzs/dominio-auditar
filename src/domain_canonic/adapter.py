from __future__ import annotations

from typing import Any, Dict, Optional

from .models import CanonicalFiscalEvent, FiscalOperation, MoneyAmounts, Party


def build_canonical_event_from_parsed(
    *,
    company_id: int,
    nota_id: Optional[int],
    parsed: Dict[str, Any],
    regime: str,
    activity_type: str,
    xml_origem: str = "",
) -> CanonicalFiscalEvent:
    """Adapter temporário: transforma o parser atual (dict simples) em um CanonicalFiscalEvent.

    Nesta fase inicial, ainda não há granularidade por item/parcela.
    O objetivo é alinhar o futuro engine de regras com um modelo único.
    """

    numero = str(parsed.get("numero") or "")
    data_emissao = str(parsed.get("data_emissao") or "")
    doc_tipo = str(parsed.get("tipo") or "saida")

    operacao = FiscalOperation(
        doc_tipo=doc_tipo,
        cfop=str(parsed.get("cfop") or ""),
        regime=regime,
        activity_type=activity_type,
    )

    emitente = Party(
        cnpj_cpf=str(parsed.get("emitente_cnpj") or ""),
        nome=str(parsed.get("emitente_nome") or ""),
    )
    destinatario = Party(
        cnpj_cpf=str(parsed.get("destinatario_cnpj") or ""),
        nome=str(parsed.get("destinatario_nome") or ""),
    )

    amounts = MoneyAmounts(
        total=float(parsed.get("valor_total") or 0.0),
        pis=float(parsed.get("valor_pis") or 0.0),
        cofins=float(parsed.get("valor_cofins") or 0.0),
        icms=float(parsed.get("valor_icms") or 0.0),
        iss=float(parsed.get("valor_iss") or 0.0),
        irpj=float(parsed.get("valor_irpj") or 0.0),
        csll=float(parsed.get("valor_csll") or 0.0),
        outras_retencoes=float(parsed.get("outras_retencoes") or 0.0),
    )

    event_key = f"{company_id}|{nota_id or 'na'}|{doc_tipo}|{numero}".strip()

    return CanonicalFiscalEvent(
        event_key=event_key,
        company_id=company_id,
        nota_id=nota_id,
        numero=numero,
        data_emissao=data_emissao,
        operacao=operacao,
        emitente=emitente,
        destinatario=destinatario,
        amounts=amounts,
        xml_origem=xml_origem or str(parsed.get("xml_origem") or ""),
        taxes=[],
        inconsistencies=[],
        debug={"adapter": "build_canonical_event_from_parsed"},
    )

