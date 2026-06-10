# -*- coding: utf-8 -*
from src.database.session import engine, Base, get_session
from src.models.base import Organization, Company, User, Product, Supplier
from src.models.fiscal import FiscalMovement, FiscalMovementItem, TaxAssessment, FiscalXml
from src.models.audit import MotorFiscalResultado, AuditAlert, SystemLog
from src.models.ncm_referencia import NcmReferencia
from datetime import datetime

def initialize_database():
    print('Iniciando inicializacao do banco de dados...')
    Base.metadata.create_all(bind=engine)
    print('Tabelas criadas com sucesso!')
    session = get_session()
    try:
        if session.query(Organization).first():
            print('O banco ja possui dados. Pulando seed.')
            return
        print('Criando dados iniciais (Seed)...')
        escritorio = Organization(name='Escritorio Contabil Exemplo', cnpj='12345678000100', created_at=datetime.utcnow())
        session.add(escritorio)
        session.flush()
        admin = User(empresa_gestora_id=escritorio.id, nome='Administrador do Sistema', email='admin@escritorio.com', senha_hash='hash_seguro_aqui', perfil='Admin', ativo=True)
        session.add(admin)
        cliente = Company(cnpj='98765432000199', razao_social='Cliente de Teste Ltda', nome_fantasia='Teste Ltda', regime_tributario='SIMPLES', uf='SP', municipio='Sao Paulo', ativo=True)
        session.add(cliente)
        session.commit()
        print('Dados iniciais criados com sucesso!')
    except Exception as e:
        session.rollback()
        print(f'Erro ao criar dados iniciais: {e}')
    finally:
        session.close()

if __name__ == '__main__':
    initialize_database()
