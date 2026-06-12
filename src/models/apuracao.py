from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base

class Apuracao(Base):
    __tablename__ = 'apuracoes'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)

    # Compatibilidade com o banco existente (fiscal_erp.db):
    # apuracoes.competencia existe, mas apuracoes.mes/ano não existem.
    competencia = Column(String(7), nullable=False)  # ex: '2026-05'

    tipo_imposto = Column(String(20), nullable=False)  # 'ICMS', 'PIS', 'COFINS', 'SIMPLES'
    # Nomes compatíveis com o schema existente no fiscal_erp.db
    total_debitos = Column(Numeric(18, 2), default=0)
    total_creditos = Column(Numeric(18, 2), default=0)
    saldo = Column(Numeric(18, 2), default=0)
    # O schema existente no fiscal_erp.db não possui apuracoes.status
    # (mantemos apenas campos que existem na tabela)
    criado_em = Column(DateTime, default=datetime.utcnow)

    itens = relationship('ApuracaoItem', back_populates='apuracao')

class ApuracaoItem(Base):
    __tablename__ = 'apuracao_itens'
    id = Column(Integer, primary_key=True)
    apuracao_id = Column(Integer, ForeignKey('apuracoes.id'), nullable=False)
    movimento_id = Column(Integer, ForeignKey('movimentos.id'), nullable=True)
    item_movimento_id = Column(Integer, ForeignKey('itens_movimento.id'), nullable=True)

    tipo_operacao = Column(String(20))  # 'debito', 'credito'
    valor_base = Column(Numeric(15, 2), default=0)
    valor_imposto = Column(Numeric(15, 2), default=0)

    apuracao = relationship('Apuracao', back_populates='itens')

class AjusteApuracao(Base):
    __tablename__ = 'ajustes_apuracao'
    id = Column(Integer, primary_key=True)
    apuracao_id = Column(Integer, ForeignKey('apuracoes.id'), nullable=False)
    descricao = Column(String(255))
    valor = Column(Numeric(15, 2), nullable=False)
    tipo = Column(String(20))  # 'acrescimo', 'reducao'
    data_ajuste = Column(DateTime, default=datetime.utcnow)

