"""Adiciona coluna tipo_documento em movimentos."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / 'fiscal_erp.db'


def run():
    if not DB_PATH.exists():
        print(f'Banco nao encontrado: {DB_PATH}')
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cols = {row[1] for row in cur.execute('PRAGMA table_info(movimentos)').fetchall()}
    if 'tipo_documento' not in cols:
        cur.execute('ALTER TABLE movimentos ADD COLUMN tipo_documento VARCHAR(10)')
        print('Coluna tipo_documento adicionada.')
    else:
        print('Coluna tipo_documento ja existe.')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    run()
