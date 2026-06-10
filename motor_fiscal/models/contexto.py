from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from decimal import Decimal

@dataclass
class ContextoFiscal:
    item_id: int
    company_id: int
    regime_tributario: str
    uf_origem: str
    uf_destino: str
    ncm: str
    cfop: str
    cst: str
    cst_pis: str
    cst_cofins: str
    valor_item: Decimal
    quantidade: Decimal
    produto_descricao: str
    csosn: str = ""
    cst_ipi: str = ""
    extras: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResultadoFiscal:
    item_id: int
    gera_credito: bool = False
    gera_debito: bool = False
    monofasico: bool = False
    substituicao_tributaria: bool = False
    valor_icms: Decimal = Decimal('0.00')
    valor_pis: Decimal = Decimal('0.00')
    valor_cofins: Decimal = Decimal('0.00')
    valor_ipi: Decimal = Decimal('0.00')
    motivo: str = ''
    alertas: List[str] = field(default_factory=list)
    alertas_auditoria: List[dict] = field(default_factory=list)

