from __future__ import annotations

from typing import Any, Dict, List

from .models import CanonicalFiscalEvent, TaxResult


def distribute_legacy_competence_result_to_event(event: CanonicalFiscalEvent, resultado: Any) -> CanonicalFiscalEvent:
    """Distribui um resultado legado (calculado por competência) para o evento.

    Nesta fase inicial, como ainda não temos granularidade por nota,
    faremos distribuição proporcional simples usando 'valor_total'.

    Retorna o evento com taxes preenchidas (mesmo que seja uma estimativa).
    Isso habilita a futura troca por regras reais.
    """

    # Placeholder proporcional: taxa total = total da competência * (valor evento / soma notas)
    # Como não temos soma aqui, aplicamos 100% no evento (para facilitar o fluxo).
    # Em etapas seguintes, vamos:
    # - carregar todas as notas do período
    # - somar receitas
    # - dividir impostos proporcionalmente
    
    base = float(event.amounts.total or 0.0)

    def add_tax(name: str, base_amount: float, rate_percent: float, debit: float, credit: float, total: float) -> None:
        event.taxes.append(
            TaxResult(
                tax=name,
                base=base_amount,
                rate_percent=rate_percent,
                debit=debit,
                credit=credit,
                total=total,
            )
        )

    # Mapeamento mínimo dos campos do ResultadoImpostos
    # Observação: seu CalculadoraTributaria tem nomes diferentes para Simples e para lucro presumido/real.
    # Este adapter só tenta preencher o que existir.
    if getattr(resultado, "das", 0) and getattr(event.operacao, "regime", "") == "simples":
        add_tax("DAS (Simples)", base, 0.0, float(resultado.das), 0.0, float(resultado.das))
    else:
        # Tributos sobre faturamento / lucro (estimado)
        if hasattr(resultado, "pis"):
            add_tax("PIS", base, 1.65, float(resultado.pis), 0.0, float(resultado.pis))
        if hasattr(resultado, "cofins"):
            add_tax("COFINS", base, 7.6, float(resultado.cofins), 0.0, float(resultado.cofins))
        if hasattr(resultado, "icms") and float(getattr(resultado, "icms", 0) or 0) != 0:
            add_tax("ICMS", base, 0.0, float(resultado.icms), 0.0, float(resultado.icms))
        if hasattr(resultado, "iss") and float(getattr(resultado, "iss", 0) or 0) != 0:
            add_tax("ISS", base, 0.0, float(resultado.iss), 0.0, float(resultado.iss))

        if hasattr(resultado, "irpj") and float(getattr(resultado, "irpj", 0) or 0) != 0:
            add_tax("IRPJ", base, 0.0, float(resultado.irpj), 0.0, float(resultado.irpj))
        if hasattr(resultado, "csll") and float(getattr(resultado, "csll", 0) or 0) != 0:
            add_tax("CSLL", base, 0.0, float(resultado.csll), 0.0, float(resultado.csll))

        # Reforma 2026 se existir
        if hasattr(resultado, "cbs_transicao"):
            add_tax("CBS (Transição 2026)", base, 0.9, float(resultado.cbs_transicao), float(resultado.cbs_transicao), 0.0)
        if hasattr(resultado, "ibs_transicao"):
            add_tax("IBS (Transição 2026)", base, 0.1, float(resultado.ibs_transicao), float(resultado.ibs_transicao), 0.0)

    return event

