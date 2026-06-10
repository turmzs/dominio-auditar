from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.ncm import get_monofasicos_ncms
from motor_fiscal.auditorias.helpers import aplica_regras_ncm

def regra_monofasico_indevido(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_ncm(contexto):
        return
    monofasicos = get_monofasicos_ncms()
    if contexto.ncm in monofasicos:
        # Mark as monofasico
        resultado.monofasico = True
        
        # Monofasico items should not have debito or credito in PIS/COFINS or ICMS under certain regimes.
        # Check PIS/COFINS CST
        if contexto.cst_pis not in ['04', '06', '07', '08', '09'] and contexto.cst_pis:
            resultado.alertas_auditoria.append({
                'tipo': 'Tributacao Monofasica',
                'severidade': 'error',
                'descricao': f'Produto monofasico ({contexto.ncm}) com CST PIS ({contexto.cst_pis}) incompativel (deveria ser 04, 06, 07 ou 09)',
                'regra_id': 'monofasico_cst_pis_incompativel'
            })
        if contexto.cst_cofins not in ['04', '06', '07', '08', '09'] and contexto.cst_cofins:
            resultado.alertas_auditoria.append({
                'tipo': 'Tributacao Monofasica',
                'severidade': 'error',
                'descricao': f'Produto monofasico ({contexto.ncm}) com CST COFINS ({contexto.cst_cofins}) incompativel (deveria ser 04, 06, 07 ou 09)',
                'regra_id': 'monofasico_cst_cofins_incompativel'
            })
