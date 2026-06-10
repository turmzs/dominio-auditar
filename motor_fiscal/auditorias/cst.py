from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.helpers import aplica_regras_icms_pis_cofins

def regra_cst_regime_compatibilidade(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_icms_pis_cofins(contexto):
        return
    regime = contexto.regime_tributario.upper()
    
    if regime == 'SIMPLES':
        if contexto.cst and not contexto.csosn:
            resultado.alertas_auditoria.append({
                'tipo': 'Regime Tributario',
                'severidade': 'warning',
                'descricao': f'Empresa do Simples Nacional utilizando CST ({contexto.cst}) em vez de CSOSN',
                'regra_id': 'simples_usando_cst'
            })
        if contexto.cst == '60':
            resultado.alertas_auditoria.append({
                'tipo': 'Regime Tributario',
                'severidade': 'error',
                'descricao': 'Empresa do Simples Nacional utilizando CST 60 (deveria ser CSOSN 500)',
                'regra_id': 'simples_cst_60'
            })
    elif regime in ['REAL', 'PRESUMIDO']:
        if contexto.csosn and not contexto.cst:
            resultado.alertas_auditoria.append({
                'tipo': 'Regime Tributario',
                'severidade': 'warning',
                'descricao': f'Empresa do Regime Normal utilizando CSOSN ({contexto.csosn}) em vez de CST',
                'regra_id': 'normal_usando_csosn'
            })
