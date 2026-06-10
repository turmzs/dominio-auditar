from decimal import Decimal
from src.database.session import get_session
from src.models.base import Company
from src.models.fiscal import FiscalMovement, FiscalMovementItem
from src.models.apuracao import Apuracao, ApuracaoItem

class ApuracaoEngine:
    def __init__(self, company_id):
        self.company_id = company_id
        self.session = get_session()

    def _preparar_apuracao(self, mes, ano, imposto):
        """Localiza ou cria o registro de apuração mensal"""
        apuracao = self.session.query(Apuracao).filter(
            Apuracao.empresa_id == self.company_id,
            Apuracao.mes == mes,
            Apuracao.ano == ano,
            Apuracao.imposto == imposto
        ).first()

        if not apuracao:
            apuracao = Apuracao(
                empresa_id=self.company_id,
                mes=mes,
                ano=ano,
                imposto=imposto,
                status='aberto'
            )
            self.session.add(apuracao)
            self.session.flush()

        self.session.query(ApuracaoItem).filter(ApuracaoItem.apuracao_id == apuracao.id).delete()
        return apuracao

    def calcular_icms(self, mes, ano):
        company = self.session.query(Company).filter(Company.id == self.company_id).first()
        if not company: raise ValueError("Empresa não encontrada")

        apuracao = self._preparar_apuracao(mes, ano, 'ICMS')
        movimentos = self.session.query(FiscalMovement).filter(
            FiscalMovement.empresa_id == self.company_id,
            FiscalMovement.data_emissao >= f'{ano}-{mes:02d}-01'
        ).all()

        total_debito = Decimal('0.00')
        total_credito = Decimal('0.00')

        for mov in movimentos:
            itens = self.session.query(FiscalMovementItem).filter(FiscalMovementItem.movimento_id == mov.id).all()
            for item in itens:
                valor_imposto = Decimal(str(item.valor_icms or 0))
                if mov.tipo_movimento == 'SAIDA':
                    tipo = 'debito'
                    total_debito += valor_imposto
                elif mov.tipo_movimento == 'ENTRADA':
                    if company.regime_tributario == 'SIMPLES': continue
                    tipo = 'credito'
                    total_credito += valor_imposto
                else: continue

                self.session.add(ApuracaoItem(
                    apuracao_id=apuracao.id, movimento_id=mov.id, item_movimento_id=item.id,
                    tipo_operacao=tipo, valor_base=Decimal(str(item.base_icms or 0)), valor_imposto=valor_imposto
                ))

        apuracao.valor_total_debito = total_debito
        apuracao.valor_total_credito = total_credito
        apuracao.valor_final = total_debito - total_credito
        self.session.commit()
        return apuracao

    def calcular_pis_cofins(self, mes, ano, imposto='PIS'):
        """Imposto pode ser 'PIS' ou 'COFINS'"""
        company = self.session.query(Company).filter(Company.id == self.company_id).first()
        if not company: raise ValueError("Empresa não encontrada")

        apuracao = self._preparar_apuracao(mes, ano, imposto)
        movimentos = self.session.query(FiscalMovement).filter(
            FiscalMovement.empresa_id == self.company_id,
            FiscalMovement.data_emissao >= f'{ano}-{mes:02d}-01'
        ).all()

        total_debito = Decimal('0.00')
        total_credito = Decimal('0.00')

        for mov in movimentos:
            itens = self.session.query(FiscalMovementItem).filter(FiscalMovementItem.movimento_id == mov.id).all()
            for item in itens:
                # Pega o valor correto baseado no imposto solicitado
                valor_imposto = Decimal(str(item.valor_pis if imposto == 'PIS' else item.valor_cofins or 0))
                valor_base = Decimal(str(item.base_pis if imposto == 'PIS' else item.base_cofins or 0))

                # Regra de Monofásico: Se for monofásico, não gera débito nem crédito
                # Aqui assumimos que a auditoria já maruou o item ou que checamos o CST
                if item.cst_pis in ['04', '06'] if imposto == 'PIS' else item.cst_cofins in ['04', '06']:
                    continue

                if mov.tipo_movimento == 'SAIDA':
                    tipo = 'debito'
                    total_debito += valor_imposto
                elif mov.tipo_movimento == 'ENTRADA':
                    # Só gera crédito se for Lucro Real (Não Cumulativo)
                    if company.regime_tributario != 'LUCRO_REAL': continue
                    tipo = 'credito'
                    total_credito += valor_imposto
                else: continue

                self.session.add(ApuracaoItem(
                    apuracao_id=apuracao.id, movimento_id=mov.id, item_movimento_id=item.id,
                    tipo_operacao=tipo, valor_base=valor_base, valor_imposto=valor_imposto
                ))

        apuracao.valor_total_debito = total_debito
        apuracao.valor_total_credito = total_credito
        apuracao.valor_final = total_debito - total_credito
        self.session.commit()
        return apuracao

    def calcular_simples(self, mes, ano):
        """Cálculo do Simples Nacional baseado no Faturamento Bruto"""
        company = self.session.query(Company).filter(Company.id == self.company_id).first()
        if company.regime_tributario != 'SIMPLES':
            raise ValueError("Empresa não está no regime Simples Nacional")

        apuracao = self._preparar_apuracao(mes, ano, 'SIMPLES')

        # Soma total de todas as saídas (Faturamento Bruto)
        movimentos_saida = self.session.query(FiscalMovement).filter(
            FiscalMovement.empresa_id == self.company_id,
            FiscalMovement.tipo_movimento == 'SAIDA',
            FiscalMovement.data_emissao >= f'{ano}-{mes:02d}-01'
        ).all()

        faturamento_bruto = Decimal('0.00')
        for mov in movimentos_saida:
            faturamento_bruto += Decimal(str(mov.valor_total or 0))

        # Alíquota simplificada (Ex: 4% para comércio).
        # Em um sistema real, isso buscaria a faixa de faturamento dos últimos 12 meses.
        aliquota = Decimal('0.04')
        valor_imposto = faturamento_bruto * aliquota

        apuracao.valor_total_debito = valor_imposto
        apuracao.valor_total_credito = Decimal('0.00')
        apuracao.valor_final = valor_imposto

        # Registro simplificado: um item representando o faturamento total
        self.session.add(ApuracaoItem(
            apuracao_id=apuracao.id,
            tipo_operacao='debito',
            valor_base=faturamento_bruto,
            valor_imposto=valor_imposto
        ))

        self.session.commit()
        return apuracao
