import sqlite3
import os

def run_migration():
    # Use the absolute path relative to the file's dir or local project dir
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'fiscal_erp.db')
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check/Add columns to 'itens_movimento'
    cursor.execute("PRAGMA table_info(itens_movimento)")
    columns = [col[1] for col in cursor.fetchall()]

    new_cols_itens = {
        'csosn': 'TEXT',
        'cst_ipi': 'TEXT',
        'base_ipi': 'REAL',
        'valor_ipi': 'REAL'
    }

    for col_name, col_type in new_cols_itens.items():
        if col_name not in columns:
            print(f"Adding column '{col_name}' to 'itens_movimento'")
            cursor.execute(f"ALTER TABLE itens_movimento ADD COLUMN {col_name} {col_type}")

    # 2. Check/Add columns to 'auditorias'
    cursor.execute("PRAGMA table_info(auditorias)")
    columns_auditorias = [col[1] for col in cursor.fetchall()]

    new_cols_audit = {
        'item_id': 'INTEGER',
        'regra_id': 'TEXT'
    }

    for col_name, col_type in new_cols_audit.items():
        if col_name not in columns_auditorias:
            print(f"Adding column '{col_name}' to 'auditorias'")
            cursor.execute(f"ALTER TABLE auditorias ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()
    print("Migration finished successfully.")

if __name__ == '__main__':
    run_migration()
