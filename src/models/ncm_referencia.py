from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime
from datetime import datetime
from src.database.session import Base

class NcmReferencia(Base):
    __tablename__ = 'ncm_referencia'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)
    descricao = Column(Text)
    monofasico_pis_cofins = Column(Boolean, default=False)
    ex_tipi = Column(String(10))
    aliquota_ipi = Column(Numeric(5, 2))
    atualizado_em = Column(DateTime, default=datetime.utcnow)
