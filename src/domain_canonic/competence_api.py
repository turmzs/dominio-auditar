from __future__ import annotations

from typing import Any, Dict

from database import DatabaseManager
from .adapter import build_canonical_event_from_parsed
from .competence_calculator_adapter import distribute_legacy_competence_result_to_event


def calculate_competence_events(*, db: DatabaseManager, empresa_id: int, mes: int, ano: int) -> Dict[str, Any]:

    """Calcula por competência e aplica no evento canônico (fase inicial).

    Nesta fase inicial:
    - ainda não distribuímos corretamente por nota/item
    - criamos um evento agregado (evento único) com soma do período

    Isso permite evoluir sem quebrar sua API atual.
    """

    empresa = db.obter_empresa(empresa_id)
    if not empresa:
        raise ValueError("Empresa não encontrada")

    totais = db.obter_totais_periodo(empresa_id, mes, ano)

    # Criar evento agregado
    parsed = {
        "id": None,
        "numero": f"AGREGADO_{mes:02d}_{ano}",
        "data_emissao": f"{ano:04d}-{mes:02d}-01",
        "tipo": "saida",
        "emitente_cnpj": empresa.get("cnpj"),
        "emitente_nome": empresa.get("nome"),
        "destinatario_cnpj": "",
        "destinatario_nome": "",
        "cfop": "",
        "valor_total": totais.get("receita_bruta", 0),
        "valor_pis": totais.get("creditos_pis", 0),
        "valor_cofins": totais.get("creditos_cofins", 0),
        "valor_csll": 0,
        "valor_irpj": 0,
        "valor_iss": 0,
        "valor_icms": 0,
        "outras_retencoes": 0,
        "xml_origem": "competencia",
    }

    event = build_canonical_event_from_parsed(
        company_id=empresa_id,
        nota_id=None,
        parsed=parsed,
        regime=str(empresa.get("regime") or ""),
        activity_type=str(empresa.get("atividade") or ""),

        xml_origem="competencia",
    )

    from calculadora import CalculadoraTributaria

    resultado = CalculadoraTributaria.calcular(
        regime=empresa["regime"],
        mes=mes,
        ano=ano,
        receita_bruta=totais["receita_bruta"],
        custos=totais["custos"],
        despesas=totais["despesas"],
        creditos_pis=totais["creditos_pis"],
        creditos_cofins=totais["creditos_cofins"],
        icms_saida=totais["icms_saida"],
        icms_entrada=totais["icms_entrada"],
        faturamento_anual=totais["faturamento_anual_acumulado"],
        folha_anual=empresa["folha_anual"],
        activity_type=empresa["atividade"],
        prejuizo_fiscal=0,
    )

    event = distribute_legacy_competence_result_to_event(event=event, resultado=resultado)
    event.debug["competence"] = {"mes": mes, "ano": ano}
    return {"event": event}

