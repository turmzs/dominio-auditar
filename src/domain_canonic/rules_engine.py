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
        from calculadora import CalculadoraTributaria

        # Map de atividade atual
        activity_type = event.operacao.activity_type
        if not activity_type:
            activity_type = "servicos"

        # Como o modelo atual só traz "total" e não traz separação de custos/despesas por evento,
        # chamamos o motor no nível competência (não evento). Por isso, nesta fase o engine
        # não altera valores de taxes; ele só deixa trace indicando necessidade de agregação.
        #
        # Para manter compatibilidade agora, geramos inconsistency indicando que a engine deve operar
        # na competência (faturamento) e não por nota.
        event.inconsistencies.append(
            "RulesEngineV1 (fase 1): cálculo ainda é de competência; evento ainda não calculado granularmente"
        )
        event.debug["mes"] = mes
        event.debug["ano"] = ano
        event.debug["motor"] = "CalculadoraTributaria (a integrar na próxima iteração)"

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

