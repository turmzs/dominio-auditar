"""Regras de auditoria especificas para NFS-e."""

import re

from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.helpers import is_servico


def regra_nfse_codigo_servico(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not is_servico(contexto):
        return

    codigo = (contexto.extras.get('codigo_servico') or '').strip()
    if not codigo:
        resultado.alertas_auditoria.append({
            'tipo': 'NFS-e',
            'severidade': 'warning',
            'descricao': 'Codigo do servico (LC 116) nao identificado no XML',
            'regra_id': 'nfse_codigo_servico_ausente',
        })
        return

    normalizado = codigo.replace('.', '').replace('-', '')
    if not re.match(r'^\d{4,6}$', normalizado):
        resultado.alertas_auditoria.append({
            'tipo': 'NFS-e',
            'severidade': 'warning',
            'descricao': f'Codigo de servico "{codigo}" fora do padrao esperado (ex: 17.01)',
            'regra_id': 'nfse_codigo_servico_formato',
        })


def regra_nfse_iss(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not is_servico(contexto):
        return

    valor_iss = contexto.extras.get('valor_iss', 0)
    if valor_iss and float(valor_iss) > 0:
        resultado.motivo += '[ISS informado] '
