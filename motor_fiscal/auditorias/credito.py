from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.helpers import aplica_regras_icms_pis_cofins

def regra_credito_simples_nacional(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_icms_pis_cofins(contexto):
        return
    regime = contexto.regime_tributario.upper()
    if regime == 'SIMPLES':
        # Simples Nacional does not generate ICMS/PIS/COFINS credit directly to be offset unless specifically allowed (which is rare)
        if resultado.gera_credito or resultado.valor_icms > 0:
            # Let's check if the result generated credit
            resultado.alertas_auditoria.append({
                'tipo': 'Credito Indevido',
                'severidade': 'error',
                'descricao': 'Empresa do Simples Nacional tentando aproveitar creditos fiscais de ICMS/PIS/COFINS',
                'regra_id': 'credito_indevido_simples'
            })

def regra_credito_cst_60(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_icms_pis_cofins(contexto):
        return
    # CST 60 means ICMS paid by Substitution, hence no credit.
    if contexto.cst == '60' and (resultado.gera_credito or resultado.valor_icms > 0):
        resultado.alertas_auditoria.append({
            'tipo': 'Credito Indevido',
            'severidade': 'error',
            'descricao': 'Tentativa de aproveitamento de credito de ICMS em item com CST 60 (ICMS retido por Substituicao Tributaria)',
            'regra_id': 'credito_item_st_cst60'
        })
