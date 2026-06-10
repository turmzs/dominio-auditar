from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.helpers import aplica_regras_difal

def regra_difal_necessidade(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_difal(contexto):
        return
    uf_origem = contexto.uf_origem
    uf_destino = contexto.uf_destino
    cfop = contexto.cfop
    
    if not cfop or len(cfop) < 1:
        return
        
    first_digit = cfop[0]
    
    # Operacao interestadual (CFOP inicia com 2, 6 ou 7)
    if first_digit in ['2', '6'] and uf_origem != uf_destino and uf_origem != 'SABER' and uf_destino != 'SABER':
        # Se for venda interestadual para consumidor final (CFOPs como 6107, 6108, etc. ou indicado em extras)
        # Para fins de demonstracao/auditoria, se o CFOP for de venda interestadual (ex: 6108)
        if cfop in ['6107', '6108']:
            # Deve haver calculo de DIFAL ou recolhimento
            if not contexto.extras.get('difal_calculado') and not resultado.valor_ipi: # Exemplo de condicao
                resultado.alertas_auditoria.append({
                    'tipo': 'DIFAL',
                    'severidade': 'warning',
                    'descricao': f'Operacao interestadual ({cfop}) com UF destino {uf_destino} pode exigir calculo e recolhimento do DIFAL',
                    'regra_id': 'difal_pendente'
                })
