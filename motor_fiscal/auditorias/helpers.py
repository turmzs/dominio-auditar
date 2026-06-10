"""Helpers para aplicar regras conforme o tipo de documento fiscal."""

from motor_fiscal.models.contexto import ContextoFiscal

TIPOS_MERCADORIA = frozenset({'NFE', 'NFCE'})
TIPOS_SERVICO = frozenset({'NFSE'})
TIPOS_TRANSPORTE = frozenset({'CTE', 'MDFE'})


def tipo_documento(contexto: ContextoFiscal) -> str:
    return (contexto.extras.get('tipo_documento') or 'NFE').upper()


def is_mercadoria(contexto: ContextoFiscal) -> bool:
    return tipo_documento(contexto) in TIPOS_MERCADORIA


def is_servico(contexto: ContextoFiscal) -> bool:
    return tipo_documento(contexto) in TIPOS_SERVICO


def is_transporte(contexto: ContextoFiscal) -> bool:
    return tipo_documento(contexto) in TIPOS_TRANSPORTE


def aplica_regras_ncm(contexto: ContextoFiscal) -> bool:
    return is_mercadoria(contexto)


def aplica_regras_icms_pis_cofins(contexto: ContextoFiscal) -> bool:
    return is_mercadoria(contexto) or is_transporte(contexto)


def aplica_regras_cfop_mercadoria(contexto: ContextoFiscal) -> bool:
    return is_mercadoria(contexto)


def aplica_regras_difal(contexto: ContextoFiscal) -> bool:
    return is_mercadoria(contexto)
