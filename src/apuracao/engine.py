from __future__ import annotations

from decimal import Decimal
from typing import Any

from src.database.session import get_session
from src.models.base import Company
from src.models.fiscal import FiscalMovement, FiscalMovementItem
from src.models.apuracao import Apuracao


class ApuracaoEngine:
    def __init__(self, company_id: int):
        self.company_id = int(company_id)
        self.session = get_session()

    def _finalizar(self):
        try:
            self.session.close()
        except Exception:
            pass

    def _limpar_e_inserir_itens_apuracao_sql(
        self, apuracao_id: int, itens: list[dict[str, Any]]
    ):
        """
        Fallback para schemas antigos do SQLite.
        O banco atual pode não ter a tabela `apuracao_itens`/`apuracao_items`.
        Para destravar a Fase 4, persistimos somente a apuração agregada em `apuracoes`.
        """
        # Se não houver itens, não faz nada.
        if not itens:
            return

        # Detecta tabela real apenas se existir (evita erro de schema).
        engine = self.session.get_bind()
        tabela = None
        try:
            with engine.connect() as conn:
                cur = conn.connection.cursor()
                cur.execute(
                    """SELECT name FROM sqlite_master WHERE type='table' AND name IN ('apuracao_itens','apuracao_items')"""
                )
                rows = cur.fetchall()
                if rows:
                    tabela = rows[0][0]
        except Exception:
            tabela = None

        # Se não existir tabela, ignora itens (UI usa apenas agregados).
        if not tabela:
            return

        with engine.connect() as conn:
            cur = conn.connection.cursor()
            cur.execute(
                f"DELETE FROM {tabela} WHERE apuracao_id = ?",
                (int(apuracao_id),),
            )

            payload = [
                (
                    int(apuracao_id),
                    it.get("movimento_id"),
                    it.get("item_movimento_id"),
                    it.get("tipo_operacao"),
                    float(it.get("valor_base") or 0),
                    float(it.get("valor_imposto") or 0),
                )
                for it in itens
            ]

            cur.executemany(
                f"""
                INSERT INTO {tabela}
                    (apuracao_id, movimento_id, item_movimento_id, tipo_operacao, valor_base, valor_imposto)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
            conn.connection.commit()

    def _preparar_apuracao(self, mes: int, ano: int, imposto: str) -> Apuracao:
        competencia = f"{int(ano)}-{int(mes):02d}"

        apuracao = (
            self.session.query(Apuracao)
            .filter(
                Apuracao.empresa_id == self.company_id,
                Apuracao.competencia == competencia,
                Apuracao.tipo_imposto == imposto,
            )
            .first()
        )

        if not apuracao:
            apuracao = Apuracao(
                empresa_id=self.company_id,
                competencia=competencia,
                tipo_imposto=imposto,
            )
            self.session.add(apuracao)
            self.session.flush()

        return apuracao

    def calcular_icms(self, mes: int, ano: int) -> Apuracao:
        try:
            company = self.session.query(Company).filter(Company.id == self.company_id).first()
            if not company:
                raise ValueError("Empresa não encontrada")

            apuracao = self._preparar_apuracao(mes, ano, "ICMS")

            movimentos = (
                self.session.query(FiscalMovement)
                .filter(
                    FiscalMovement.empresa_id == self.company_id,
                    FiscalMovement.data_emissao >= f"{ano}-{mes:02d}-01",
                )
                .all()
            )

            total_debito = Decimal("0.00")
            total_credito = Decimal("0.00")
            itens_para_inserir: list[dict[str, Any]] = []

            for mov in movimentos:
                itens = (
                    self.session.query(FiscalMovementItem)
                    .filter(FiscalMovementItem.movimento_id == mov.id)
                    .all()
                )
                for item in itens:
                    valor_imposto = Decimal(str(item.valor_icms or 0))

                    if mov.tipo_movimento == "SAIDA":
                        tipo = "debito"
                        total_debito += valor_imposto
                    elif mov.tipo_movimento == "ENTRADA":
                        if company.regime_tributario == "SIMPLES":
                            continue
                        tipo = "credito"
                        total_credito += valor_imposto
                    else:
                        continue

                    itens_para_inserir.append(
                        {
                            "movimento_id": mov.id,
                            "item_movimento_id": item.id,
                            "tipo_operacao": tipo,
                            "valor_base": Decimal(str(item.base_icms or 0)),
                            "valor_imposto": valor_imposto,
                        }
                    )

            apuracao.total_debitos = total_debito
            apuracao.total_creditos = total_credito
            apuracao.saldo = total_debito - total_credito

            self._limpar_e_inserir_itens_apuracao_sql(apuracao.id, itens_para_inserir)

            self.session.commit()
            return apuracao
        except Exception:
            self.session.rollback()
            raise
        finally:
            self._finalizar()

    def calcular_pis_cofins(self, mes: int, ano: int, imposto: str = "PIS") -> Apuracao:
        try:
            company = self.session.query(Company).filter(Company.id == self.company_id).first()
            if not company:
                raise ValueError("Empresa não encontrada")

            apuracao = self._preparar_apuracao(mes, ano, imposto)

            movimentos = (
                self.session.query(FiscalMovement)
                .filter(
                    FiscalMovement.empresa_id == self.company_id,
                    FiscalMovement.data_emissao >= f"{ano}-{mes:02d}-01",
                )
                .all()
            )

            total_debito = Decimal("0.00")
            total_credito = Decimal("0.00")
            itens_para_inserir: list[dict[str, Any]] = []

            for mov in movimentos:
                itens = (
                    self.session.query(FiscalMovementItem)
                    .filter(FiscalMovementItem.movimento_id == mov.id)
                    .all()
                )
                for item in itens:
                    valor_imposto = Decimal(
                        str(item.valor_pis if imposto == "PIS" else item.valor_cofins or 0)
                    )
                    valor_base = Decimal(
                        str(item.base_pis if imposto == "PIS" else item.base_cofins or 0)
                    )

                    # Regra monofásico: ignora quando CST indica não incidência/monofásico
                    if (
                        (imposto == "PIS" and item.cst_pis in ["04", "06"])
                        or (imposto == "COFINS" and item.cst_cofins in ["04", "06"])
                    ):
                        continue

                    if mov.tipo_movimento == "SAIDA":
                        tipo = "debito"
                        total_debito += valor_imposto
                    elif mov.tipo_movimento == "ENTRADA":
                        if company.regime_tributario != "LUCRO_REAL":
                            continue
                        tipo = "credito"
                        total_credito += valor_imposto
                    else:
                        continue

                    itens_para_inserir.append(
                        {
                            "movimento_id": mov.id,
                            "item_movimento_id": item.id,
                            "tipo_operacao": tipo,
                            "valor_base": valor_base,
                            "valor_imposto": valor_imposto,
                        }
                    )

            apuracao.total_debitos = total_debito
            apuracao.total_creditos = total_credito
            apuracao.saldo = total_debito - total_credito

            self._limpar_e_inserir_itens_apuracao_sql(apuracao.id, itens_para_inserir)

            self.session.commit()
            return apuracao
        except Exception:
            self.session.rollback()
            raise
        finally:
            self._finalizar()

    def calcular_simples(self, mes: int, ano: int) -> Apuracao:
        try:
            company = self.session.query(Company).filter(Company.id == self.company_id).first()
            if not company or company.regime_tributario != "SIMPLES":
                raise ValueError("Empresa não está no regime Simples Nacional")

            apuracao = self._preparar_apuracao(mes, ano, "SIMPLES")

            movimentos_saida = (
                self.session.query(FiscalMovement)
                .filter(
                    FiscalMovement.empresa_id == self.company_id,
                    FiscalMovement.tipo_movimento == "SAIDA",
                    FiscalMovement.data_emissao >= f"{ano}-{mes:02d}-01",
                )
                .all()
            )

            faturamento_bruto = Decimal("0.00")
            for mov in movimentos_saida:
                faturamento_bruto += Decimal(str(mov.valor_total or 0))

            aliquota = Decimal("0.04")
            valor_imposto = faturamento_bruto * aliquota

            apuracao.total_debitos = valor_imposto
            apuracao.total_creditos = Decimal("0.00")
            apuracao.saldo = valor_imposto

            itens_para_inserir = [
                {
                    "movimento_id": None,
                    "item_movimento_id": None,
                    "tipo_operacao": "debito",
                    "valor_base": faturamento_bruto,
                    "valor_imposto": valor_imposto,
                }
            ]

            self._limpar_e_inserir_itens_apuracao_sql(apuracao.id, itens_para_inserir)

            self.session.commit()
            return apuracao
        except Exception:
            self.session.rollback()
            raise
        finally:
            self._finalizar()
