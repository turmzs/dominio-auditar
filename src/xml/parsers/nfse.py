"""Parser NFS-e — layouts ABRASF, Ginfes e padrão nacional (infNFSe / DPS)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from src.xml.parsers.base import (
    ParsedDocument,
    clean_digits,
    empty_item,
    find_elements,
    first_text,
    parse_date,
    resolve_direction,
    to_float,
)
from src.xml.parsers.detector import DOC_NFSE


def parse_nfse(root: ET.Element, company_cnpj: str | None = None) -> ParsedDocument:
    if find_elements(root, 'infNFSe') or find_elements(root, 'infDPS'):
        return _parse_nfse_nacional(root, company_cnpj)
    return _parse_nfse_abrasf(root, company_cnpj)


def _party_cnpj(block: ET.Element | None) -> tuple[str, str]:
    if block is None:
        return '', ''
    cnpj = clean_digits(
        first_text(block, 'Cnpj')
        or first_text(block, 'CNPJ')
        or first_text(block, 'CpfCnpj')
        or first_text(block, 'Cpf')
    )
    nome = (
        first_text(block, 'RazaoSocial')
        or first_text(block, 'xNome')
        or first_text(block, 'Nome')
    )
    return cnpj, nome


def _parse_nfse_abrasf(root: ET.Element, company_cnpj: str | None) -> ParsedDocument:
    inf = (
        find_elements(root, 'InfNfse')
        or find_elements(root, 'infNFSe')
        or find_elements(root, 'Nfse')
    )
    scope = inf[0] if inf else root

    prest = find_elements(scope, 'PrestadorServico') or find_elements(scope, 'Prestador')
    tom = find_elements(scope, 'TomadorServico') or find_elements(scope, 'Tomador')
    prest_id = find_elements(prest[0], 'IdentificacaoPrestador') if prest else []
    tom_id = find_elements(tom[0], 'IdentificacaoTomador') if tom else []

    prest_cnpj, prest_nome = _party_cnpj(prest_id[0] if prest_id else (prest[0] if prest else None))
    if prest and not prest_nome:
        prest_nome = first_text(prest[0], 'RazaoSocial')

    tom_cnpj, tom_nome = _party_cnpj(tom_id[0] if tom_id else (tom[0] if tom else None))
    if tom and not tom_nome:
        tom_nome = first_text(tom[0], 'RazaoSocial')

    numero = (
        first_text(scope, 'Numero')
        or first_text(scope, 'nNFSe')
        or first_text(root, 'Numero')
    )
    dh = (
        first_text(scope, 'DataEmissao')
        or first_text(scope, 'DataEmissaoRps')
        or first_text(scope, 'dhProc')
    )

    itens = []
    servicos = find_elements(scope, 'Servico') or find_elements(scope, 'serv')
    if not servicos:
        servicos = [scope]

    for serv in servicos:
        item = empty_item()
        item['codigo_servico'] = (
            first_text(serv, 'ItemListaServico')
            or first_text(serv, 'CodigoTributacaoMunicipio')
            or first_text(serv, 'cTribNac')
        )
        item['descricao'] = (
            first_text(serv, 'Discriminacao')
            or first_text(serv, 'xDescServ')
            or f'Servico {item["codigo_servico"]}'.strip()
        )
        valores = find_elements(serv, 'Valores')
        val_scope = valores[0] if valores else serv
        item['valor_total'] = to_float(
            first_text(val_scope, 'ValorServicos')
            or first_text(val_scope, 'vServ')
            or first_text(val_scope, 'ValorLiquidoNfse')
        )
        item['valor_unitario'] = item['valor_total']
        item['valor_iss'] = to_float(
            first_text(val_scope, 'ValorIss')
            or first_text(val_scope, 'vISS')
        )
        item['valor_pis'] = to_float(first_text(val_scope, 'ValorPis'))
        item['valor_cofins'] = to_float(first_text(val_scope, 'ValorCofins'))
        item['valor_irpj'] = to_float(first_text(val_scope, 'ValorIr'))
        item['valor_csll'] = to_float(first_text(val_scope, 'ValorCsll'))
        item['cfop'] = first_text(serv, 'CFOP') or '5933'
        if item['descricao'] or item['codigo_servico']:
            itens.append(item)

    if not itens:
        item = empty_item()
        item['descricao'] = 'Servico prestado (NFS-e)'
        item['codigo_servico'] = '00.00'
        item['valor_total'] = to_float(
            first_text(scope, 'ValorLiquidoNfse')
            or first_text(scope, 'ValorServicos')
        )
        item['valor_unitario'] = item['valor_total']
        itens.append(item)

    valor_total = sum(i['valor_total'] for i in itens)
    valor_iss = sum(i.get('valor_iss', 0) for i in itens)

    return ParsedDocument(
        doc_tipo=DOC_NFSE,
        layout='abrasf',
        numero=numero,
        serie=first_text(scope, 'Serie') or first_text(root, 'Serie'),
        access_key=clean_digits(first_text(scope, 'CodigoVerificacao') or first_text(scope, 'Id')),
        data_emissao=parse_date(dh),
        tipo=resolve_direction(company_cnpj, prest_cnpj, tom_cnpj, tomador_cnpj=tom_cnpj, prestador_cnpj=prest_cnpj),
        emitente_cnpj=prest_cnpj,
        emitente_nome=prest_nome,
        destinatario_cnpj=tom_cnpj,
        destinatario_nome=tom_nome,
        cfop='5933',
        valor_total=valor_total,
        valor_produtos=0.0,
        valor_icms=0.0,
        valor_ipi=0.0,
        valor_pis=sum(i.get('valor_pis', 0) for i in itens),
        valor_cofins=sum(i.get('valor_cofins', 0) for i in itens),
        valor_iss=valor_iss,
        valor_csll=sum(i.get('valor_csll', 0) for i in itens),
        valor_irpj=sum(i.get('valor_irpj', 0) for i in itens),
        outras_retencoes=0.0,
        itens=itens,
    )


def _parse_nfse_nacional(root: ET.Element, company_cnpj: str | None) -> ParsedDocument:
    inf = find_elements(root, 'infNFSe') or find_elements(root, 'infDPS')
    scope = inf[0] if inf else root

    emit = find_elements(scope, 'emit') or find_elements(scope, 'prest')
    dest = find_elements(scope, 'dest') or find_elements(scope, 'toma')
    emit_cnpj = clean_digits(first_text(emit[0], 'CNPJ')) if emit else ''
    emit_nome = first_text(emit[0], 'xNome') if emit else ''
    dest_cnpj = clean_digits(first_text(dest[0], 'CNPJ') or first_text(dest[0], 'CPF')) if dest else ''
    dest_nome = first_text(dest[0], 'xNome') if dest else ''

    item = empty_item()
    item['codigo_servico'] = first_text(scope, 'cTribNac') or first_text(scope, 'cLocPrestacao')
    item['descricao'] = first_text(scope, 'xDescServ') or 'Servico NFS-e nacional'
    item['valor_total'] = to_float(first_text(scope, 'vServ') or first_text(scope, 'vLiq'))
    item['valor_unitario'] = item['valor_total']
    item['valor_iss'] = to_float(first_text(scope, 'vISS'))

    return ParsedDocument(
        doc_tipo=DOC_NFSE,
        layout='nacional',
        numero=first_text(scope, 'nNFSe') or first_text(scope, 'nDPS'),
        serie=first_text(scope, 'serie'),
        access_key=clean_digits(first_text(scope, 'Id')),
        data_emissao=parse_date(first_text(scope, 'dhEmi') or first_text(scope, 'dhProc')),
        tipo=resolve_direction(company_cnpj, emit_cnpj, dest_cnpj),
        emitente_cnpj=emit_cnpj,
        emitente_nome=emit_nome,
        destinatario_cnpj=dest_cnpj,
        destinatario_nome=dest_nome,
        cfop='5933',
        valor_total=item['valor_total'],
        valor_produtos=0.0,
        valor_icms=0.0,
        valor_ipi=0.0,
        valor_pis=0.0,
        valor_cofins=0.0,
        valor_iss=item['valor_iss'],
        valor_csll=0.0,
        valor_irpj=0.0,
        outras_retencoes=0.0,
        itens=[item],
    )
