"""Parser CT-e (Conhecimento de Transporte Eletrônico)."""

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
    tag_name,
    to_float,
)
from src.xml.parsers.detector import DOC_CTE


def parse_cte(root: ET.Element, company_cnpj: str | None = None) -> ParsedDocument:
    access_key = ''
    for inf in find_elements(root, 'infCte'):
        access_key = extract_key_from_id(inf.get('Id') or inf.get('id') or '', 'CTe')
        if access_key:
            break
    if not access_key:
        access_key = clean_digits(first_text(root, 'chCTe'))

    emit_el = find_elements(root, 'emit')
    dest_el = find_elements(root, 'dest') or find_elements(root, 'receb')
    rem_el = find_elements(root, 'rem')
    emit_cnpj = clean_digits(first_text(emit_el[0], 'CNPJ')) if emit_el else ''
    emit_nome = first_text(emit_el[0], 'xNome') if emit_el else ''
    dest_cnpj = ''
    dest_nome = ''
    if dest_el:
        dest_cnpj = clean_digits(first_text(dest_el[0], 'CNPJ') or first_text(dest_el[0], 'CPF'))
        dest_nome = first_text(dest_el[0], 'xNome')
    elif rem_el:
        dest_cnpj = clean_digits(first_text(rem_el[0], 'CNPJ') or first_text(rem_el[0], 'CPF'))
        dest_nome = first_text(rem_el[0], 'xNome')

    vprest = find_elements(root, 'vPrest')
    valor_total = to_float(first_text(vprest[0], 'vTPrest')) if vprest else 0.0

    cfop = first_text(root, 'CFOP')
    dh_emi = first_text(root, 'dhEmi') or first_text(root, 'dEmi')

    item = empty_item()
    item['descricao'] = (
        first_text(root, 'xObs')
        or first_text(root, 'xOutCat')
        or 'Servico de transporte (CT-e)'
    )[:500]
    item['cfop'] = cfop or '5353'
    item['quantidade'] = 1.0
    item['valor_total'] = valor_total
    item['valor_unitario'] = valor_total

    imp = find_elements(root, 'imp')
    if imp:
        for icms in find_elements(imp[0], 'ICMS'):
            for sub in icms.iter():
                t = tag_name(sub)
                if t == 'CST':
                    item['cst_icms'] = sub.text or ''
                elif t == 'vICMS':
                    item['valor_icms'] = to_float(sub.text)
                elif t == 'vBC':
                    item['base_icms'] = to_float(sub.text)

    valor_icms = item['valor_icms']

    return ParsedDocument(
        doc_tipo=DOC_CTE,
        layout='sefaz_cte_v4',
        numero=first_text(root, 'nCT'),
        serie=first_text(root, 'serie'),
        access_key=access_key,
        data_emissao=parse_date(dh_emi),
        tipo=resolve_direction(company_cnpj, emit_cnpj, dest_cnpj),
        emitente_cnpj=emit_cnpj,
        emitente_nome=emit_nome,
        destinatario_cnpj=dest_cnpj,
        destinatario_nome=dest_nome,
        cfop=item['cfop'],
        valor_total=valor_total,
        valor_produtos=0.0,
        valor_icms=valor_icms,
        valor_ipi=0.0,
        valor_pis=0.0,
        valor_cofins=0.0,
        valor_iss=0.0,
        valor_csll=0.0,
        valor_irpj=0.0,
        outras_retencoes=0.0,
        itens=[item],
        metadata={'modal': first_text(root, 'modal')},
    )
