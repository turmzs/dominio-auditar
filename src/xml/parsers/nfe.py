"""Parser NF-e (mod 55) e NFC-e (mod 65)."""

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
from src.xml.parsers.detector import DOC_NFCE, DOC_NFE, first_mod


def parse_nfe(root: ET.Element, company_cnpj: str | None = None) -> ParsedDocument:
    mod = first_mod(root)
    doc_tipo = DOC_NFCE if mod == '65' else DOC_NFE

    access_key = ''
    for inf in find_elements(root, 'infNFe'):
        access_key = extract_key_from_id(inf.get('Id') or inf.get('id') or '', 'NFe')
        if access_key:
            break
    if not access_key:
        access_key = clean_digits(first_text(root, 'chNFe'))

    emit_el = find_elements(root, 'emit')
    dest_el = find_elements(root, 'dest')
    emit_cnpj = clean_digits(first_text(emit_el[0], 'CNPJ')) if emit_el else ''
    emit_nome = first_text(emit_el[0], 'xNome') if emit_el else ''
    dest_cnpj = ''
    dest_nome = ''
    if dest_el:
        dest_cnpj = clean_digits(
            first_text(dest_el[0], 'CNPJ') or first_text(dest_el[0], 'CPF')
        )
        dest_nome = first_text(dest_el[0], 'xNome')

    dh_emi = first_text(root, 'dhEmi') or first_text(root, 'dEmi')
    tot_el = find_elements(root, 'ICMSTot')

    valor_total = to_float(first_text(tot_el[0], 'vNF')) if tot_el else 0.0
    valor_produtos = to_float(first_text(tot_el[0], 'vProd')) if tot_el else valor_total
    valor_icms = to_float(first_text(tot_el[0], 'vICMS')) if tot_el else 0.0
    valor_ipi = to_float(first_text(tot_el[0], 'vIPI')) if tot_el else 0.0
    valor_pis = to_float(first_text(tot_el[0], 'vPIS')) if tot_el else 0.0
    valor_cofins = to_float(first_text(tot_el[0], 'vCOFINS')) if tot_el else 0.0

    itens = []
    for det in find_elements(root, 'det'):
        item = _parse_det(det)
        if item['descricao'] or item['ncm']:
            itens.append(item)

    return ParsedDocument(
        doc_tipo=doc_tipo,
        layout='sefaz_nfe_v4',
        numero=first_text(root, 'nNF'),
        serie=first_text(root, 'serie'),
        access_key=access_key,
        data_emissao=parse_date(dh_emi),
        tipo=resolve_direction(company_cnpj, emit_cnpj, dest_cnpj),
        emitente_cnpj=emit_cnpj,
        emitente_nome=emit_nome,
        destinatario_cnpj=dest_cnpj,
        destinatario_nome=dest_nome,
        cfop=first_text(root, 'CFOP') or (itens[0]['cfop'] if itens else ''),
        valor_total=valor_total,
        valor_produtos=valor_produtos,
        valor_icms=valor_icms,
        valor_ipi=valor_ipi,
        valor_pis=valor_pis,
        valor_cofins=valor_cofins,
        valor_iss=0.0,
        valor_csll=0.0,
        valor_irpj=0.0,
        outras_retencoes=0.0,
        itens=itens,
        metadata={'mod': mod or ('65' if doc_tipo == DOC_NFCE else '55')},
    )


def _parse_det(det: ET.Element) -> dict:
    item = empty_item()
    prod = find_elements(det, 'prod')
    imp = find_elements(det, 'imposto')
    prod_el = prod[0] if prod else det

    item['descricao'] = first_text(prod_el, 'xProd')
    item['ncm'] = first_text(prod_el, 'NCM')
    item['cfop'] = first_text(prod_el, 'CFOP')
    qtd = first_text(prod_el, 'qCom') or first_text(prod_el, 'qCmd', '1')
    item['quantidade'] = to_float(qtd, 1.0)
    item['valor_unitario'] = to_float(first_text(prod_el, 'vUnCom'))
    item['valor_total'] = to_float(first_text(prod_el, 'vProd'))

    if imp:
        _parse_imposto(imp[0], item)
    return item


def _parse_imposto(imp_el: ET.Element, item: dict) -> None:
    icms_el = find_elements(imp_el, 'ICMS')
    if icms_el:
        for sub in icms_el[0].iter():
            t = tag_name(sub)
            if t == 'CST':
                item['cst_icms'] = sub.text or ''
            elif t == 'CSOSN':
                item['csosn'] = sub.text or ''
            elif t == 'vICMS':
                item['valor_icms'] = to_float(sub.text)
            elif t == 'vBC':
                item['base_icms'] = to_float(sub.text)

    for block, cst_key, base_key, val_key in (
        ('PIS', 'cst_pis', 'base_pis', 'valor_pis'),
        ('COFINS', 'cst_cofins', 'base_cofins', 'valor_cofins'),
    ):
        blk = find_elements(imp_el, block)
        if blk:
            for sub in blk[0].iter():
                t = tag_name(sub)
                if t == 'CST':
                    item[cst_key] = sub.text or ''
                elif t == 'vBC':
                    item[base_key] = to_float(sub.text)
                elif t == 'vPIS' or t == 'vCOFINS':
                    item[val_key] = to_float(sub.text)

    ipi_el = find_elements(imp_el, 'IPI')
    if ipi_el:
        for sub in ipi_el[0].iter():
            t = tag_name(sub)
            if t == 'CST':
                item['cst_ipi'] = sub.text or ''
            elif t == 'vBC':
                item['base_ipi'] = to_float(sub.text)
            elif t == 'vIPI':
                item['valor_ipi'] = to_float(sub.text)
