from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Date, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base

class FiscalMovement(Base):
    __tablename__ = 'movimentos'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    chave_nfe = Column(String(44), unique=True)
    numero_nota = Column(String(20), nullable=False)
    serie = Column(String(10))
    tipo_documento = Column(String(10))
    tipo_movimento = Column(String(20))
    data_emissao = Column(Date)
    data_entrada = Column(Date)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'))
    valor_total = Column(Numeric(18, 2))
    valor_produtos = Column(Numeric(18, 2))
    valor_icms = Column(Numeric(18, 2))
    valor_ipi = Column(Numeric(18, 2))
    valor_pis = Column(Numeric(18, 2))
    valor_cofins = Column(Numeric(18, 2))
    situacao = Column(String(30))
    criado_em = Column(DateTime, default=datetime.utcnow)
    items = relationship('FiscalMovementItem', back_populates='movement')

class FiscalMovementItem(Base):
    __tablename__ = 'itens_movimento'
    id = Column(Integer, primary_key=True)
    movimento_id = Column(Integer, ForeignKey('movimentos.id'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    descricao = Column(String(500))
    cfop = Column(String(4))
    cst_icms = Column(String(3))
    cst_pis = Column(String(3))
    cst_cofins = Column(String(3))
    csosn = Column(String(4))
    cst_ipi = Column(String(3))
    base_ipi = Column(Numeric(18, 2))
    valor_ipi = Column(Numeric(18, 2))
    ncm = Column(String(10))
    quantidade = Column(Numeric(18, 4))
    valor_unitario = Column(Numeric(18, 6))
    valor_total = Column(Numeric(18, 2))
    base_icms = Column(Numeric(18, 2))
    valor_icms = Column(Numeric(18, 2))
    base_pis = Column(Numeric(18, 2))
    valor_pis = Column(Numeric(18, 2))
    base_cofins = Column(Numeric(18, 2))
    valor_cofins = Column(Numeric(18, 2))
    movement = relationship('FiscalMovement', back_populates='items')

class TaxAssessment(Base):
    __tablename__ = 'apuracoes'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    competencia = Column(String(7))
    tipo_imposto = Column(String(30))
    total_creditos = Column(Numeric(18, 2))
    total_debitos = Column(Numeric(18, 2))
    saldo = Column(Numeric(18, 2))
    criado_em = Column(DateTime, default=datetime.utcnow)

class FiscalXml(Base):
    __tablename__ = 'xmls'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    chave_nfe = Column(String(44))
    caminho_arquivo = Column(Text)
    hash_arquivo = Column(Text)
    processado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
