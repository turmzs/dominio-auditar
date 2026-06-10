"""Parser MDF-e (Manifesto Eletrônico de Documentos Fiscais)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from src.xml.parsers.base import (
    ParsedDocument,
    clean_digits,
    empty_item,
    extract_key_from_id,
    find_elements,
    first_text,
    parse_date,
    resolve_direction,
    to_float,
)
from src.xml.parsers.detector import DOC_MDFE


def parse_mdfe(root: ET.Element, company_cnpj: str | None = None) -> ParsedDocument:
    access_key = ''
    for inf in find_elements(root, 'infMDFe'):
        access_key = extract_key_from_id(inf.get('Id') or inf.get('id') or '', 'MDFe')
        if access_key:
            break

    emit_el = find_elements(root, 'emit')
    emit_cnpj = clean_digits(first_text(emit_el[0], 'CNPJ')) if emit_el else ''
    emit_nome = first_text(emit_el[0], 'xNome') if emit_el else ''

    tot = find_elements(root, 'tot')
    q_nfe = first_text(tot[0], 'qNFe') if tot else '0'
    q_cte = first_text(tot[0], 'qCTe') if tot else '0'
    valor_carga = to_float(first_text(tot[0], 'vCarga')) if tot else 0.0

    item = empty_item()
    item['descricao'] = f'MDF-e — {q_nfe} NF-e(s), {q_cte} CT-e(s) vinculados'
    item['valor_total'] = valor_carga
    item['valor_unitario'] = valor_carga
    item['cfop'] = ''

    dh_emi = first_text(root, 'dhEmi') or first_text(root, 'dEmi')

    return ParsedDocument(
        doc_tipo=DOC_MDFE,
        layout='sefaz_mdfe_v3',
        numero=first_text(root, 'nMDF'),
        serie=first_text(root, 'serie'),
        access_key=access_key,
        data_emissao=parse_date(dh_emi),
        tipo=resolve_direction(company_cnpj, emit_cnpj, ''),
        emitente_cnpj=emit_cnpj,
        emitente_nome=emit_nome,
        destinatario_cnpj='',
        destinatario_nome='',
        cfop='',
        valor_total=valor_carga,
        valor_produtos=0.0,
        valor_icms=0.0,
        valor_ipi=0.0,
        valor_pis=0.0,
        valor_cofins=0.0,
        valor_iss=0.0,
        valor_csll=0.0,
        valor_irpj=0.0,
        outras_retencoes=0.0,
        itens=[item],
        metadata={'qNFe': q_nfe, 'qCTe': q_cte},
    )
