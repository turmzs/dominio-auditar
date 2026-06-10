"""
Fachada de compatibilidade — delega para o motor unificado em src/xml/parsers/.

Mantém parse_xml_invoice() para código legado (app.py, importer_service).
"""

from __future__ import annotations

from src.xml.parsers.registry import parse_xml_document


def parse_xml_invoice(xml_content_or_path, company_cnpj=None):
    try:
        doc = parse_xml_document(xml_content_or_path, company_cnpj=company_cnpj)
        if not doc:
            return None
        return doc.to_dict()
    except ValueError as exc:
        print(f'Erro ao analisar XML: {exc}')
        return None
