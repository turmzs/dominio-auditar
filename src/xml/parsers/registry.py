"""Ponto de entrada unificado para parsing de XML fiscal."""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Union

from src.xml.parsers.base import ParsedDocument
from src.xml.parsers.cte import parse_cte
from src.xml.parsers.detector import (
    DOC_CTE,
    DOC_DESCONHECIDO,
    DOC_EVENTO,
    DOC_MDFE,
    DOC_NFE,
    DOC_NFCE,
    DOC_NFSE,
    detect_document_type,
)
from src.xml.parsers.mdfe import parse_mdfe
from src.xml.parsers.nfe import parse_nfe
from src.xml.parsers.nfse import parse_nfse

XmlInput = Union[str, bytes]


def load_root(xml_content_or_path: XmlInput) -> ET.Element:
    if isinstance(xml_content_or_path, str):
        if os.path.exists(xml_content_or_path):
            return ET.parse(xml_content_or_path).getroot()
        return ET.fromstring(xml_content_or_path)
    if isinstance(xml_content_or_path, bytes):
        return ET.fromstring(xml_content_or_path)
    raise ValueError('Formato de XML invalido')


def parse_xml_document(xml_content_or_path: XmlInput, company_cnpj: str | None = None) -> ParsedDocument | None:
    try:
        root = load_root(xml_content_or_path)
        doc_type = detect_document_type(root)

        if doc_type in (DOC_NFE, DOC_NFCE):
            doc = parse_nfe(root, company_cnpj)
            doc.doc_tipo = doc_type
            return doc
        if doc_type == DOC_NFSE:
            return parse_nfse(root, company_cnpj)
        if doc_type == DOC_CTE:
            return parse_cte(root, company_cnpj)
        if doc_type == DOC_MDFE:
            return parse_mdfe(root, company_cnpj)
        if doc_type == DOC_EVENTO:
            raise ValueError('XML de evento fiscal nao gera movimento. Importe o documento principal (NF-e, CT-e etc.).')

        raise ValueError(
            'Tipo de documento nao reconhecido. Suportados: NF-e, NFC-e, NFS-e, CT-e e MDF-e.'
        )
    except ValueError:
        raise
    except Exception as exc:
        print(f'Erro ao analisar XML: {exc}')
        return None


def supported_document_types() -> list[dict[str, str]]:
    return [
        {'id': 'NFE', 'label': 'NF-e (modelo 55)', 'parser': 'sefaz_nfe_v4'},
        {'id': 'NFCE', 'label': 'NFC-e (modelo 65)', 'parser': 'sefaz_nfe_v4'},
        {'id': 'NFSE', 'label': 'NFS-e (ABRASF / Nacional)', 'parser': 'abrasf|nacional'},
        {'id': 'CTE', 'label': 'CT-e', 'parser': 'sefaz_cte_v4'},
        {'id': 'MDFE', 'label': 'MDF-e', 'parser': 'sefaz_mdfe_v3'},
    ]
