from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    regime_tributario = Column(String(50))
    uf = Column(String(2))
    municipio = Column(String(100))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    products = relationship('Product', back_populates='company')
    suppliers = relationship('Supplier', back_populates='company')

class User(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    empresa_gestora_id = Column(Integer, ForeignKey('organizations.id'))
    nome = Column(String(150))
    email = Column(String(255), unique=True)
    senha_hash = Column(Text)
    perfil = Column(String(50))
    ativo = Column(Boolean, default=True)

class Supplier(Base):
    __tablename__ = 'fornecedores'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    cnpj = Column(String(14))
    razao_social = Column(String(255))
    company = relationship('Company', back_populates='suppliers')

class Product(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    codigo = Column(String(60))
    descricao = Column(Text)
    ncm = Column(String(10))
    cest = Column(String(10))
    criado_em = Column(DateTime, default=datetime.utcnow)
    company = relationship('Company', back_populates='products')
