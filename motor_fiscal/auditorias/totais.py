from motor_fiscal.engine.executor import FiscalExecutor

def verificar_totais_nota(executor, movimento_id):
    """
    Verifica se a soma dos itens do movimento condiz com o valor total da nota.
    """
    session = executor.session
    from src.models.fiscal import FiscalMovement, FiscalMovementItem
    
    mov = session.query(FiscalMovement).filter(FiscalMovement.id == movimento_id).first()
    if not mov:
        return []

    itens = session.query(FiscalMovementItem).filter(FiscalMovementItem.movimento_id == movimento_id).all()
    soma_itens = sum(item.valor_total for item in itens)
    total_nota = mov.valor_total or 0

    divergencia = abs(soma_itens - total_nota)
    
    # Tolerância de 0.01 para arredondamentos
    if divergencia > 0.01:
        return [{
            'regra_id': 'TOTAL_DIVERGENTE',
            'tipo': 'Soma Itens vs Total Nota',
            'severidade': 'critico',
            'descricao': f'A soma dos itens (R${soma_itens:.2f}) diverge do valor total da nota (R${total_nota:.2f}). Diferença: R${divergencia:.2f}',
            'item_id': None # Alerta nível nota
        }]
    
    return []