"""
Módulo de escrita fiscal: transformação de notas fiscais em lançamentos fiscais
Author: Copilot CLI
"""
from typing import List, Dict


def gerar_escritura_fiscal(db, empresa_id: int, mes: int, ano: int) -> List[Dict]:
    """Gera a escrituração fiscal (lista de lançamentos) a partir das notas do período e persiste no DB.

    Args:
        db: Instância de DatabaseManager
        empresa_id: id da empresa
        mes, ano: competência

    Returns:
        Lista de dicionários representando os lançamentos fiscais gerados.
    """
    notas = db.listar_notas(empresa_id, mes, ano, tipo=None)
    entries = []

    for idx, n in enumerate(notas, start=1):
        entry = {
            "linha": idx,
            "nota_id": n.get("id"),
            "data_emissao": n.get("data_emissao"),
            "numero": n.get("numero"),
            "tipo": n.get("tipo"),
            "cfop": n.get("cfop"),
            "valor_total": n.get("valor_total", 0.0),
            "impostos": {
                "pis": n.get("valor_pis", 0.0),
                "cofins": n.get("valor_cofins", 0.0),
                "csll": n.get("valor_csll", 0.0),
                "irpj": n.get("valor_irpj", 0.0),
                "iss": n.get("valor_iss", 0.0),
                "icms": n.get("valor_icms", 0.0),
                "outras_retencoes": n.get("outras_retencoes", 0.0)
            },
            # Conta fiscal heurística (exemplo; projeto pode ajustar para plano de contas real)
            "conta": ("Receita de Serviços" if (n.get("cfop", "").startswith("5") or n.get("tipo") == "saida") else "Receita de Vendas")
        }

        # Ajustes heurísticos para entradas (custos/despesas) — marca como custo quando tipo == entrada
        if n.get("tipo") == "entrada":
            entry["conta"] = "Compra de Mercadorias/Serviços (Custo/Despesa)"

        entries.append(entry)

    # Persistir no banco
    try:
        db.salvar_escritura_fiscal(empresa_id, mes, ano, entries)
    except Exception:
        pass

    return entries
