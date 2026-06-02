from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class MoneyAmounts:
    total: float = 0.0
    pis: float = 0.0
    cofins: float = 0.0
    icms: float = 0.0
    iss: float = 0.0
    irpj: float = 0.0
    csll: float = 0.0
    outras_retencoes: float = 0.0


@dataclass(frozen=True)
class Party:
    cnpj_cpf: str = ""
    nome: str = ""


@dataclass(frozen=True)
class FiscalOperation:
    doc_tipo: str  # entrada | saida
    cfop: str = ""
    regime: str = ""  # simples | presumido | real
    activity_type: str = ""  # comercio | servicos | fator_r


@dataclass(frozen=True)
class RuleTrace:
    rule_id: str
    rule_version: str
    rule_name: str = ""
    description: str = ""
    applied_to: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaxResult:
    tax: str  # PIS/COFINS/ICMS/ISS/IRPJ/CSLL/CBS/IBS/...
    base: float
    rate_percent: float
    debit: float
    credit: float
    total: float
    trace: Optional[RuleTrace] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CanonicalFiscalEvent:
    # Identificação
    event_key: str  # empresa_id|nota_id|tipo
    company_id: int
    nota_id: Optional[int]
    numero: str
    data_emissao: str

    # Identidade fiscal / operação
    operacao: FiscalOperation
    emitente: Party
    destinatario: Party

    # Valores e retenções (extraído do XML)
    amounts: MoneyAmounts
    xml_origem: str = ""

    # Resultados por cálculo (derivados do motor de regras)
    taxes: List[TaxResult] = field(default_factory=list)
    inconsistencies: List[str] = field(default_factory=list)

    # Auditoria do evento (memória detalhada)
    debug: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompetenceSummary:
    company_id: int
    mes: int
    ano: int
    totals: Dict[str, float] = field(default_factory=dict)
    events_count: int = 0

