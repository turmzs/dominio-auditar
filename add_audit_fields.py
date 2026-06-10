from src.database.session import engine, Base, get_session
from src.models.audit import AuditAlert
import sqlalchemy as sa

def upgrade():
    conn = engine.connect()
    
    # Verifica se a coluna status já existe
    inspector = sa.inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('auditorias')]
    
    if 'status' not in columns:
        conn.execute(sa.text('ALTER TABLE auditorias ADD COLUMN status VARCHAR(20) DEFAULT \'pendente\''))
        print('Coluna status adicionada.')
    else:
        print('Coluna status ja existe.')
        
    if 'observacao' not in columns:
        conn.execute(sa.text('ALTER TABLE auditorias ADD COLUMN observacao TEXT'))
        print('Coluna observacao adicionada.')
    else:
        print('Coluna observacao ja existe.')
        
    conn.close()
    print('Migracao concluida com sucesso.')

if __name__ == '__main__':
    upgrade()
