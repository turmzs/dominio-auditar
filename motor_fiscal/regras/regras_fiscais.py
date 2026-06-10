from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.ncm import get_monofasicos_ncms
from motor_fiscal.auditorias.helpers import aplica_regras_icms_pis_cofins, is_servico

def regra_icms_basica(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if is_servico(contexto):
        resultado.motivo += '[NFS-e: tributacao por ISS] '
        return
    if not aplica_regras_icms_pis_cofins(contexto):
        return
    monofasicos = get_monofasicos_ncms()
    if contexto.ncm in monofasicos:
        resultado.monofasico = True
        resultado.motivo += '[NCM Monofasico] '
    if contexto.cst == '60':
        resultado.substituicao_tributaria = True
        resultado.gera_credito = False
        resultado.motivo += '[CST 60: ST] '
    elif contexto.cst == '00':
        resultado.gera_debito = True
        resultado.motivo += '[CST 00: Tributado] '
    if contexto.regime_tributario == 'SIMPLES':
        resultado.gera_credito = False
        resultado.motivo += '[Simples: Sem Credito] '

def regra_pis_cofins(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if is_servico(contexto) or not aplica_regras_icms_pis_cofins(contexto):
        return
    if contexto.cst_pis == '01' or contexto.cst_cofins == '01':
        resultado.gera_debito = True
        resultado.motivo += '[PIS/COFINS: Tributado] '
    elif contexto.cst_pis in ['06', '07'] or contexto.cst_cofins in ['06', '07']:
        resultado.monofasico = True
        resultado.motivo += '[PIS/COFINS: Monofasico/Substituido] '

def regra_auditoria_conflitos(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if is_servico(contexto) or not aplica_regras_icms_pis_cofins(contexto):
        return
    if resultado.monofasico and contexto.cst == '00':
        resultado.alertas.append('Conflito: Item marcado como Monofasico mas CST ICMS eh 00 (Tributado)')
