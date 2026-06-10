from motor_fiscal.auditorias.ncm import regra_ncm_vazio_ou_invalido, regra_ncm_monofasico_tributacao
from motor_fiscal.auditorias.cfop import regra_cfop_direcao, regra_cfop_uf
from motor_fiscal.auditorias.cst import regra_cst_regime_compatibilidade
from motor_fiscal.auditorias.monofasico import regra_monofasico_indevido
from motor_fiscal.auditorias.credito import regra_credito_simples_nacional, regra_credito_cst_60
from motor_fiscal.auditorias.difal import regra_difal_necessidade
from motor_fiscal.auditorias.nfse import regra_nfse_codigo_servico, regra_nfse_iss

def get_all_audit_rules():
    """Retorna todas as regras de auditoria registradas"""
    return [
        regra_ncm_vazio_ou_invalido,
        regra_ncm_monofasico_tributacao,
        regra_cfop_direcao,
        regra_cfop_uf,
        regra_cst_regime_compatibilidade,
        regra_monofasico_indevido,
        regra_credito_simples_nacional,
        regra_credito_cst_60,
        regra_difal_necessidade,
        regra_nfse_codigo_servico,
        regra_nfse_iss,
    ]
