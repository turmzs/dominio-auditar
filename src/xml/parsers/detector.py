"""Detecta o tipo de documento fiscal a partir do XML."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from src.xml.parsers.base import find_elements, tag_name

DOC_NFE = 'NFE'
DOC_NFCE = 'NFCE'
DOC_NFSE = 'NFSE'
DOC_CTE = 'CTE'
DOC_MDFE = 'MDFE'
DOC_EVENTO = 'EVENTO'
DOC_DESCONHECIDO = 'DESCONHECIDO'


def detect_document_type(root: ET.Element) -> str:
    root_name = tag_name(root)

    if _has_any(root, ('infNFe',)) or root_name in ('NFe', 'nfeProc'):
        mod = first_mod(root)
        if mod == '65':
            return DOC_NFCE
        return DOC_NFE

    if _has_any(root, ('infCte',)) or root_name in ('CTe', 'cteProc'):
        return DOC_CTE

    if _has_any(root, ('infMDFe',)) or root_name in ('MDFe', 'mdfeProc'):
        return DOC_MDFE

    if _has_any(root, ('infEvento', 'retEvento', 'procEventoNFe', 'procEventoCTe')):
        return DOC_EVENTO

    if (
        _has_any(root, ('CompNfse', 'InfNfse', 'Nfse', 'infNFSe', 'DPS', 'infDPS'))
        or root_name in ('CompNfse', 'NFSe', 'NFSe', 'Rps')
        or _has_any(root, ('IdentificacaoRps', 'Servico', 'PrestadorServico'))
    ):
        return DOC_NFSE

    return DOC_DESCONHECIDO


def first_mod(root: ET.Element) -> str:
    for ide in find_elements(root, 'ide'):
        for child in ide:
            if tag_name(child) == 'mod' and child.text:
                return child.text.strip()
    for mod in find_elements(root, 'mod'):
        if mod.text:
            return mod.text.strip()
    return ''


def _has_any(root: ET.Element, names: tuple[str, ...]) -> bool:
    wanted = set(names)
    for el in root.iter():
        if tag_name(el) in wanted:
            return True
    return False
