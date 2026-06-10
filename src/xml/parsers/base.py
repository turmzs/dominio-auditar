"""Utilitários e contrato canônico para parsers de documentos fiscais XML."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
import re
import xml.etree.ElementTree as ET
from typing import Any


def tag_name(element: ET.Element) -> str:
    return element.tag.split('}')[-1]


def find_elements(element: ET.Element, name: str) -> list[ET.Element]:
    return [el for el in element.iter() if tag_name(el) == name]


def first_text(element: ET.Element, name: str, default: str = '') -> str:
    els = find_elements(element, name)
    if els and els[0].text:
        return els[0].text.strip()
    return default


def clean_digits(value: str) -> str:
    return re.sub(r'\D', '', value or '')


def to_float(value: str | float | int | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(str(value).replace(',', '.') or default)
    except (TypeError, ValueError):
        return default


def parse_date(raw: str) -> str:
    if not raw:
        return datetime.now().strftime('%Y-%m-%d')
    return raw[:10]


def extract_key_from_id(id_attr: str, prefix: str) -> str:
    if not id_attr:
        return ''
    cleaned = id_attr.replace(prefix, '')
    return clean_digits(cleaned)


def resolve_direction(
    company_cnpj: str | None,
    emitente_cnpj: str,
    destinatario_cnpj: str,
    tomador_cnpj: str = '',
    prestador_cnpj: str = '',
) -> str:
    comp = clean_digits(company_cnpj or '')
    if not comp:
        return 'saida'
    if comp and comp == clean_digits(destinatario_cnpj or tomador_cnpj):
        return 'entrada'
    if comp and comp == clean_digits(emitente_cnpj or prestador_cnpj):
        return 'saida'
    return 'saida'


def empty_item() -> dict[str, Any]:
    return {
        'descricao': '',
        'ncm': '',
        'codigo_servico': '',
        'cfop': '',
        'quantidade': 1.0,
        'valor_unitario': 0.0,
        'valor_total': 0.0,
        'cst_icms': '',
        'csosn': '',
        'cst_pis': '',
        'cst_cofins': '',
        'cst_ipi': '',
        'base_icms': 0.0,
        'valor_icms': 0.0,
        'base_pis': 0.0,
        'valor_pis': 0.0,
        'base_cofins': 0.0,
        'valor_cofins': 0.0,
        'base_ipi': 0.0,
        'valor_ipi': 0.0,
        'valor_iss': 0.0,
    }


@dataclass
class ParsedDocument:
  doc_tipo: str
  layout: str
  numero: str
  serie: str
  access_key: str
  data_emissao: str
  tipo: str
  emitente_cnpj: str
  emitente_nome: str
  destinatario_cnpj: str
  destinatario_nome: str
  cfop: str
  valor_total: float
  valor_produtos: float
  valor_icms: float
  valor_ipi: float
  valor_pis: float
  valor_cofins: float
  valor_iss: float
  valor_csll: float
  valor_irpj: float
  outras_retencoes: float
  itens: list[dict[str, Any]] = field(default_factory=list)
  xml_origem: str = ''
  metadata: dict[str, Any] = field(default_factory=dict)

  def to_dict(self) -> dict[str, Any]:
    data = asdict(self)
    data['doc_tipo'] = self.doc_tipo.lower()
    return data
