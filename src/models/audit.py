from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base

class MotorFiscalResultado(Base):
    __tablename__ = 'motor_fiscal_resultado'
    id = Column(Integer, primary_key=True)
    item_movimento_id = Column(Integer, ForeignKey('itens_movimento.id'), nullable=False)
    gera_credito = Column(Boolean, default=False)
    gera_debito = Column(Boolean, default=False)
    monofasico = Column(Boolean, default=False)
    substituicao_tributaria = Column(Boolean, default=False)
    motivo = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    item = relationship('FiscalMovementItem')

class AuditAlert(Base):
    __tablename__ = 'auditorias'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    movimento_id = Column(Integer, ForeignKey('movimentos.id'))
    item_id = Column(Integer, ForeignKey('itens_movimento.id'))
    regra_id = Column(String(100))
    tipo = Column(String(100))
    severidade = Column(String(20))
    descricao = Column(Text)
    status = Column(String(20), default='pendente')
    observacao = Column(Text)
    resolvido = Column(Boolean, default=False) # mantido para compatibilidade
    criado_em = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    tabela = Column(String(100))
    registro_id = Column(Integer)
    acao = Column(String(30))
    valor_anterior = Column(JSON)
    valor_novo = Column(JSON)
    criado_em = Column(DateTime, default=datetime.utcnow)

