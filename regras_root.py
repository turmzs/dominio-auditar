from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal

NCM_MONOFASICOS = ['12345678', '87654321']

def regra_icms_basica(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if contexto.ncm in NCM_MONOFASICOS:
        resultado.monofasico = True
        resultado.motivo += '[NCM Monofasico detectado] '

    if contexto.cst == '60':
        resultado.substituicao_tributaria = True
        resultado.gera_credito = False
        resultado.motivo += '[CST 60: ICMS ST] '
    elif contexto.cst == '00':
        resultado.gera_debito = True
        resultado.motivo += '[CST 00: Tributado Integral] '

    if contexto.regime_tributario == 'SIMPLES':
        resultado.gera_credito = False
        resultado.motivo += '[Regime Simples: Sem credito de ICMS] '