import sys
import os
from decimal import Decimal

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.ncm import regra_ncm_vazio_ou_invalido, regra_ncm_monofasico_tributacao
from motor_fiscal.auditorias.cfop import regra_cfop_direcao, regra_cfop_uf
from motor_fiscal.auditorias.cst import regra_cst_regime_compatibilidade
from motor_fiscal.auditorias.monofasico import regra_monofasico_indevido
from motor_fiscal.auditorias.credito import regra_credito_simples_nacional, regra_credito_cst_60
from motor_fiscal.auditorias.difal import regra_difal_necessidade

def test_regra_ncm_vazio():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='REAL',
        uf_origem='SP', uf_destino='SP', ncm='', cfop='5102',
        cst='00', cst_pis='01', cst_cofins='01',
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste'
    )
    resultado = ResultadoFiscal(item_id=1)
    regra_ncm_vazio_ou_invalido(contexto, resultado)
    
    assert len(resultado.alertas_auditoria) == 1
    assert resultado.alertas_auditoria[0]['regra_id'] == 'ncm_vazio'
    assert resultado.alertas_auditoria[0]['severidade'] == 'critical'

def test_regra_ncm_invalido():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='REAL',
        uf_origem='SP', uf_destino='SP', ncm='12345', cfop='5102',
        cst='00', cst_pis='01', cst_cofins='01',
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste'
    )
    resultado = ResultadoFiscal(item_id=1)
    regra_ncm_vazio_ou_invalido(contexto, resultado)
    
    assert len(resultado.alertas_auditoria) == 1
    assert resultado.alertas_auditoria[0]['regra_id'] == 'ncm_invalido'
    assert resultado.alertas_auditoria[0]['severidade'] == 'error'

def test_regra_cfop_direcao_incompativel():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='REAL',
        uf_origem='SP', uf_destino='SP', ncm='12345678', cfop='1102', # CFOP de entrada
        cst='00', cst_pis='01', cst_cofins='01',
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste',
        extras={'tipo_movimento': 'saida'} # Movimento de saida
    )
    resultado = ResultadoFiscal(item_id=1)
    regra_cfop_direcao(contexto, resultado)
    
    assert len(resultado.alertas_auditoria) == 1
    assert resultado.alertas_auditoria[0]['regra_id'] == 'cfop_saida_entrada_incompativel'

def test_regra_cfop_uf_diferente():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='REAL',
        uf_origem='SP', uf_destino='RJ', ncm='12345678', cfop='5102', # CFOP interno (inicia com 5)
        cst='00', cst_pis='01', cst_cofins='01',
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste'
    )
    resultado = ResultadoFiscal(item_id=1)
    regra_cfop_uf(contexto, resultado)
    
    assert len(resultado.alertas_auditoria) == 1
    assert resultado.alertas_auditoria[0]['regra_id'] == 'cfop_interno_uf_diferente'

def test_regra_cst_simples_nacional():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='SIMPLES',
        uf_origem='SP', uf_destino='SP', ncm='12345678', cfop='5102',
        cst='60', cst_pis='01', cst_cofins='01', csosn='',
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste'
    )
    resultado = ResultadoFiscal(item_id=1)
    regra_cst_regime_compatibilidade(contexto, resultado)
    
    # Simples usando CST (warning) e Simples com CST 60 (error)
    assert len(resultado.alertas_auditoria) == 2
    regra_ids = [a['regra_id'] for a in resultado.alertas_auditoria]
    assert 'simples_usando_cst' in regra_ids
    assert 'simples_cst_60' in regra_ids

def test_regra_monofasico_indevido():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='REAL',
        uf_origem='SP', uf_destino='SP', ncm='12345678', cfop='5102',
        cst='00', cst_pis='01', cst_cofins='01', # Tributando monofasico
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste'
    )
    resultado = ResultadoFiscal(item_id=1)
    regra_monofasico_indevido(contexto, resultado)
    
    assert resultado.monofasico is True
    assert len(resultado.alertas_auditoria) == 2 # CST PIS e COFINS incompativeis
    regra_ids = [a['regra_id'] for a in resultado.alertas_auditoria]
    assert 'monofasico_cst_pis_incompativel' in regra_ids
    assert 'monofasico_cst_cofins_incompativel' in regra_ids

def test_regra_credito_indevido_simples():
    contexto = ContextoFiscal(
        item_id=1, company_id=1, regime_tributario='SIMPLES',
        uf_origem='SP', uf_destino='SP', ncm='12345678', cfop='1102',
        cst='', cst_pis='01', cst_cofins='01', csosn='101',
        valor_item=Decimal('100.00'), quantidade=Decimal('1'),
        produto_descricao='Produto Teste'
    )
    # Resultado com credito gerado
    resultado = ResultadoFiscal(item_id=1, gera_credito=True, valor_icms=Decimal('18.00'))
    regra_credito_simples_nacional(contexto, resultado)
    
    assert len(resultado.alertas_auditoria) == 1
    assert resultado.alertas_auditoria[0]['regra_id'] == 'credito_indevido_simples'

if __name__ == '__main__':
    print("Running tests...")
    test_regra_ncm_vazio()
    test_regra_ncm_invalido()
    test_regra_cfop_direcao_incompativel()
    test_regra_cfop_uf_diferente()
    test_regra_cst_simples_nacional()
    test_regra_monofasico_indevido()
    test_regra_credito_indevido_simples()
    print("All tests passed successfully!")
