import os
import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_path="dominio_auditar.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de Empresas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empresas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cnpj TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    regime TEXT CHECK(regime IN ('simples', 'presumido', 'real')) NOT NULL,
                    atividade TEXT CHECK(atividade IN ('comercio', 'servicos', 'fator_r')) NOT NULL,
                    faturamento_anual REAL DEFAULT 0,
                    folha_anual REAL DEFAULT 0
                )
            """)

            # Tabela de Notas Fiscais (Escrituração)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notas_fiscais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresa_id INTEGER NOT NULL,
                    numero TEXT NOT NULL,
                    data_emissao TEXT NOT NULL, -- formato YYYY-MM-DD
                    tipo TEXT CHECK(tipo IN ('entrada', 'saida')) NOT NULL,
                    emitente_cnpj TEXT,
                    emitente_nome TEXT,
                    destinatario_cnpj TEXT,
                    destinatario_nome TEXT,
                    cfop TEXT,
                    valor_total REAL DEFAULT 0,
                    valor_pis REAL DEFAULT 0,
                    valor_cofins REAL DEFAULT 0,
                    valor_csll REAL DEFAULT 0,
                    valor_irpj REAL DEFAULT 0,
                    valor_iss REAL DEFAULT 0,
                    valor_icms REAL DEFAULT 0,
                    outras_retencoes REAL DEFAULT 0,
                    xml_origem TEXT,
                    FOREIGN KEY(empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
                    UNIQUE(empresa_id, numero, tipo)
                )
            """)
            
            # Tabela para Memória de Cálculo consolidada (opcional para histórico)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memorias_calculo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresa_id INTEGER NOT NULL,
                    mes INTEGER NOT NULL,
                    ano INTEGER NOT NULL,
                    regime TEXT NOT NULL,
                    resultado_json TEXT NOT NULL,
                    FOREIGN KEY(empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
                    UNIQUE(empresa_id, mes, ano)
                )
            """)

            # Inserir empresa de teste caso o banco esteja limpo
            cursor.execute("SELECT COUNT(*) FROM empresas")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO empresas (cnpj, nome, regime, atividade, faturamento_anual, folha_anual)
                    VALUES ('12.345.678/0001-90', 'Empresa de Exemplo S/A', 'simples', 'servicos', 1500000.0, 350000.0)
                """)
            
            conn.commit()

    # Métodos de Empresas
    def listar_empresas(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empresas ORDER BY nome")
            return [dict(row) for row in cursor.fetchall()]

    def obter_empresa(self, id_empresa):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empresas WHERE id = ?", (id_empresa,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def salvar_empresa(self, nome, cnpj, regime, atividade, faturamento_anual=0, folha_anual=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO empresas (nome, cnpj, regime, atividade, faturamento_anual, folha_anual)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nome, cnpj, regime, atividade, faturamento_anual, folha_anual))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Se o CNPJ já existe, atualizar
                cursor.execute("""
                    UPDATE empresas 
                    SET nome = ?, regime = ?, atividade = ?, faturamento_anual = ?, folha_anual = ?
                    WHERE cnpj = ?
                """, (nome, regime, atividade, faturamento_anual, folha_anual, cnpj))
                conn.commit()
                cursor.execute("SELECT id FROM empresas WHERE cnpj = ?", (cnpj,))
                return cursor.fetchone()[0]

    def excluir_empresa(self, id_empresa):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM empresas WHERE id = ?", (id_empresa,))
            conn.commit()

    # Métodos de Notas Fiscais
    def salvar_nota(self, nota_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO notas_fiscais (
                        empresa_id, numero, data_emissao, tipo, emitente_cnpj, emitente_nome,
                        destinatario_cnpj, destinatario_nome, cfop, valor_total,
                        valor_pis, valor_cofins, valor_csll, valor_irpj, valor_iss, valor_icms,
                        outras_retencoes, xml_origem
                    ) VALUES (
                        :empresa_id, :numero, :data_emissao, :tipo, :emitente_cnpj, :emitente_nome,
                        :destinatario_cnpj, :destinatario_nome, :cfop, :valor_total,
                        :valor_pis, :valor_cofins, :valor_csll, :valor_irpj, :valor_iss, :valor_icms,
                        :outras_retencoes, :xml_origem
                    )
                """, nota_data)
                conn.commit()
                return True
            except Exception as e:
                print(f"Erro ao salvar nota no banco: {e}")
                return False

    def listar_notas(self, id_empresa, mes=None, ano=None, tipo=None):
        query = "SELECT * FROM notas_fiscais WHERE empresa_id = ?"
        params = [id_empresa]

        if mes and ano:
            # data_emissao está no formato YYYY-MM-DD
            query += " AND strftime('%m', data_emissao) = ? AND strftime('%Y', data_emissao) = ?"
            params.extend([f"{int(mes):02d}", str(ano)])
        elif ano:
            query += " AND strftime('%Y', data_emissao) = ?"
            params.append(str(ano))

        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)

        query += " ORDER BY data_emissao DESC, numero DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def excluir_nota(self, id_nota):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notas_fiscais WHERE id = ?", (id_nota,))
            conn.commit()

    def obter_totais_periodo(self, id_empresa, mes, ano):
        """Calcula totais de faturamento e despesas do período"""
        notas = self.listar_notas(id_empresa, mes, ano)
        
        receita_bruta = 0
        custos = 0
        despesas = 0
        creditos_pis = 0
        creditos_cofins = 0
        icms_saida = 0
        icms_entrada = 0
        iss = 0
        
        for n in notas:
            val = n['valor_total']
            if n['tipo'] == 'saida':
                receita_bruta += val
                icms_saida += n['valor_icms']
                iss += n['valor_iss']
            else: # entrada
                # Em escrituração simplificada, podemos considerar CFOPs para separar custos de despesas
                # CFOPs iniciados com 1 ou 2 ou 3 são entradas.
                # Se for compra de mercadoria para industrialização/comercialização, é CUSTO (ex: 1101, 1102, 2102, etc.)
                # Se for despesa de uso/consumo ou serviço, consideramos DESPESA.
                cfop = n['cfop'] or ''
                is_custo = any(prefix in cfop for prefix in ['1101', '1102', '2101', '2102', '3101', '3102', '1401', '1403', '2403'])
                
                if is_custo:
                    custos += val
                else:
                    despesas += val
                
                icms_entrada += n['valor_icms']
                # Crédito de PIS/COFINS (no Lucro Real Não Cumulativo, as entradas de insumos/mercadorias geram crédito)
                creditos_pis += n['valor_pis']
                creditos_cofins += n['valor_cofins']

        # Faturamento anual acumulado nos 12 meses anteriores
        faturamento_anual = self.calcular_faturamento_anual_acumulado(id_empresa, mes, ano)

        return {
            "receita_bruta": receita_bruta,
            "custos": custos,
            "despesas": despesas,
            "creditos_pis": creditos_pis,
            "creditos_cofins": creditos_cofins,
            "icms_saida": icms_saida,
            "icms_entrada": icms_entrada,
            "iss": iss,
            "faturamento_anual_acumulado": faturamento_anual
        }

    def calcular_faturamento_anual_acumulado(self, id_empresa, mes, ano):
        """Calcula o faturamento acumulado nos últimos 12 meses anteriores ao período (RBT12)"""
        # Vamos pegar todas as notas de saída nos últimos 12 meses anteriores
        # Ex: apuração em 05/2026 -> acumula de 05/2025 até 04/2026.
        # Mas para simplificar, se não houver dados, usamos o faturamento_anual cadastrado na empresa como base
        empresa = self.obter_empresa(id_empresa)
        if not empresa:
            return 0

        # Encontrar faturamento real escriturado no banco nos últimos 12 meses anteriores
        # Vamos gerar os 12 meses anteriores
        import datetime
        data_corrente = datetime.date(int(ano), int(mes), 1)
        
        faturamento_escriturado = 0
        tem_notas = False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for i in range(1, 13):
                # Subtrai i meses
                mes_sub = data_corrente.month - i
                ano_sub = data_corrente.year
                while mes_sub <= 0:
                    mes_sub += 12
                    ano_sub -= 1
                
                cursor.execute("""
                    SELECT SUM(valor_total) FROM notas_fiscais 
                    WHERE empresa_id = ? AND tipo = 'saida' 
                    AND strftime('%m', data_emissao) = ? AND strftime('%Y', data_emissao) = ?
                """, (id_empresa, f"{mes_sub:02d}", str(ano_sub)))
                
                val = cursor.fetchone()[0]
                if val is not None:
                    faturamento_escriturado += val
                    tem_notas = True

        # Se houver notas escrituradas no banco, usamos o valor escriturado.
        # Se for zero mas a empresa tem faturamento_anual cadastrado, usamos o faturamento cadastrado como estimativa de partida
        if tem_notas and faturamento_escriturado > 0:
            return faturamento_escriturado
        else:
            return empresa.get('faturamento_anual', 0)
