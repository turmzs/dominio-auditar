from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.helpers import aplica_regras_cfop_mercadoria, is_servico

def regra_cfop_direcao(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if is_servico(contexto):
        return
    if not aplica_regras_cfop_mercadoria(contexto):
        return
    tipo_movimento = contexto.extras.get('tipo_movimento', '').lower()
    cfop = contexto.cfop
    
    if not cfop:
        resultado.alertas_auditoria.append({
            'tipo': 'CFOP',
            'severidade': 'critical',
            'descricao': 'CFOP nao informado',
            'regra_id': 'cfop_vazio'
        })
        return

    first_digit = cfop[0]
    
    if tipo_movimento == 'entrada' and first_digit in ['5', '6', '7']:
        resultado.alertas_auditoria.append({
            'tipo': 'CFOP',
            'severidade': 'error',
            'descricao': f'CFOP de saida ({cfop}) utilizado em movimento de entrada',
            'regra_id': 'cfop_entrada_saida_incompativel'
        })
    elif tipo_movimento == 'saida' and first_digit in ['1', '2', '3']:
        resultado.alertas_auditoria.append({
            'tipo': 'CFOP',
            'severidade': 'error',
            'descricao': f'CFOP de entrada ({cfop}) utilizado em movimento de saida',
            'regra_id': 'cfop_saida_entrada_incompativel'
        })

def regra_cfop_uf(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if is_servico(contexto) or not aplica_regras_cfop_mercadoria(contexto):
        return
    cfop = contexto.cfop
    if not cfop or len(cfop) < 1:
        return

    first_digit = cfop[0]
    uf_origem = contexto.uf_origem
    uf_destino = contexto.uf_destino
    
    # 2 e 6 sao interestaduais
    if first_digit in ['2', '6']:
        if uf_origem == uf_destino and uf_origem != 'SABER':
            resultado.alertas_auditoria.append({
                'tipo': 'CFOP',
                'severidade': 'warning',
                'descricao': f'CFOP interestadual ({cfop}) utilizado com mesma UF origem e destino ({uf_origem})',
                'regra_id': 'cfop_interestadual_mesma_uf'
            })
    # 1 e 5 sao internos
    elif first_digit in ['1', '5']:
        if uf_origem != uf_destino and uf_origem != 'SABER' and uf_destino != 'SABER':
            resultado.alertas_auditoria.append({
                'tipo': 'CFOP',
                'severidade': 'warning',
                'descricao': f'CFOP interno ({cfop}) utilizado com UF origem ({uf_origem}) diferente de UF destino ({uf_destino})',
                'regra_id': 'cfop_interno_uf_diferente'
            })
