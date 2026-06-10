from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .models import CanonicalFiscalEvent, MemoriaCalculoItem, TaxResult, RuleTrace


# NOTE: nesta primeira versão, vamos reaproveitar os cálculos do seu CalculadoraTributaria,
# mas passando os resultados para o formato Canonical (taxes + trace).
# Em seguida, esse módulo será substituído por regras versionadas de verdade.


class RulesEngineV1:
    @staticmethod
    def calculate(event: CanonicalFiscalEvent, *, mes: int, ano: int) -> CanonicalFiscalEvent:
        from motor_fiscal.engine.executor import FiscalExecutor
        from src.models.fiscal import FiscalMovementItem
        from src.database.session import get_session

        executor = FiscalExecutor()
        session = get_session()

        if event.nota_id:
            items = session.query(FiscalMovementItem).filter(FiscalMovementItem.movimento_id == event.nota_id).all()
            for item in items:
                resultado = executor.processar_item(item.id)
                # Map resultado to event.taxes
                if resultado.valor_icms > 0 or resultado.gera_debito or resultado.gera_credito:
                    event.taxes.append(TaxResult(
                        tax="ICMS",
                        base=float(item.base_icms or 0.0),
                        rate_percent=0.0,
                        debit=float(resultado.valor_icms) if resultado.gera_debito else 0.0,
                        credit=float(resultado.valor_icms) if resultado.gera_credito else 0.0,
                        total=float(resultado.valor_icms),
                        trace=RuleTrace(
                            rule_id="ICMS_BASIC",
                            rule_version="1.0",
                            rule_name="ICMS",
                            description=resultado.motivo
                        )
                    ))
                if resultado.valor_pis > 0:
                    event.taxes.append(TaxResult(
                        tax="PIS",
                        base=float(item.base_pis or 0.0),
                        rate_percent=0.0,
                        debit=float(resultado.valor_pis) if resultado.gera_debito else 0.0,
                        credit=float(resultado.valor_pis) if resultado.gera_credito else 0.0,
                        total=float(resultado.valor_pis)
                    ))
                if resultado.valor_cofins > 0:
                    event.taxes.append(TaxResult(
                        tax="COFINS",
                        base=float(item.base_cofins or 0.0),
                        rate_percent=0.0,
                        debit=float(resultado.valor_cofins) if resultado.gera_debito else 0.0,
                        credit=float(resultado.valor_cofins) if resultado.gera_credito else 0.0,
                        total=float(resultado.valor_cofins)
                    ))
                for alert in resultado.alertas:
                    if alert not in event.inconsistencies:
                        event.inconsistencies.append(alert)

        event.debug["mes"] = mes
        event.debug["ano"] = ano
        event.debug["motor"] = "FiscalExecutor (unified)"

        return event


def legacy_aggregate_to_event_taxes(
    *,
    event: CanonicalFiscalEvent,
    resultado: Any,
) -> CanonicalFiscalEvent:
    """Quando você integrar o cálculo por competência, você vai distribuir taxes por imposto.
    Por enquanto, isso é um placeholder.
    """
    return event

