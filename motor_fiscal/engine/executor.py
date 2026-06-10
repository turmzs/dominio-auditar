from decimal import Decimal
from src.database.session import get_session
from src.models.base import Company
from src.models.fiscal import FiscalMovementItem
from src.models.audit import MotorFiscalResultado
from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal

class FiscalExecutor:
    """
    Orquestrador do Motor Fiscal. 
    Transforma dados brutos em decisões fiscais através de um pipeline de regras.
    """
    def __init__(self):
        self.session = get_session()
        self.regras = [] # Lista de funções/classes de regras a serem executadas
        self._carregar_regras_padrao()

    def _carregar_regras_padrao(self):
        try:
            from motor_fiscal.regras.regras_fiscais import regra_icms_basica, regra_pis_cofins, regra_auditoria_conflitos
            self.adicionar_regra(regra_icms_basica)
            self.adicionar_regra(regra_pis_cofins)
            self.adicionar_regra(regra_auditoria_conflitos)
        except Exception as e:
            # Em testes ou se os arquivos de auditorias mudarem
            pass

        # Bloco C: carregar também regras do registry se disponível
        try:
            from motor_fiscal.auditorias.registry import get_all_audit_rules
            for regra in get_all_audit_rules():
                self.adicionar_regra(regra)
        except Exception:
            pass

    def adicionar_regra(self, regra_func):
        """Adiciona uma nova regra ao pipeline de processamento"""
        self.regras.append(regra_func)

    def montar_contexto(self, item_id: int) -> ContextoFiscal:
        """
        Busca no banco todos os dados necessários para criar o ContextoFiscal.
        """
        item = self.session.query(FiscalMovementItem).filter(FiscalMovementItem.id == item_id).first()
        if not item:
            raise ValueError(f'Item {item_id} nao encontrado')

        empresa_id = item.movement.empresa_id
        company = self.session.query(Company).filter(Company.id == empresa_id).first()
        if not company:
            raise ValueError(f'Empresa {empresa_id} nao encontrada para o item {item_id}')

        tipo_doc = (getattr(item.movement, 'tipo_documento', None) or 'NFE').upper()
        ncm_item = item.ncm or ''
        codigo_servico = ''

        if tipo_doc == 'NFSE':
            codigo_servico = ncm_item
            ncm_item = ''

        return ContextoFiscal(
            item_id=item.id,
            company_id=company.id,
            regime_tributario=company.regime_tributario or 'SABER',
            uf_origem=company.uf or 'SABER',
            uf_destino=company.uf or 'SABER',
            ncm=ncm_item,
            cfop=item.cfop or '',
            cst=item.cst_icms or '',
            cst_pis=item.cst_pis or '',
            cst_cofins=item.cst_cofins or '',
            csosn=getattr(item, 'csosn', '') or '',
            cst_ipi=getattr(item, 'cst_ipi', '') or '',
            valor_item=Decimal(str(item.valor_total or 0)),
            quantidade=Decimal(str(item.quantidade or 0)),
            produto_descricao=item.descricao or '',
            extras={
                'tipo_movimento': item.movement.tipo_movimento or '',
                'tipo_documento': tipo_doc,
                'codigo_servico': codigo_servico,
                'valor_iss': float(item.valor_pis or 0) if tipo_doc == 'NFSE' else 0,
            },
        )

    def processar_item(self, item_id: int) -> ResultadoFiscal:
        """
        Pipeline principal: Contexto -> Regras -> Resultado
        """
        # 1. Monta o contexto (estático)
        contexto = self.montar_contexto(item_id)
        
        # 2. Inicializa o resultado (vazio)
        resultado = ResultadoFiscal(item_id=item_id)
        
        # 3. Executa cada regra do pipeline
        # Cada regra recebe o contexto e o resultado, e altera o resultado
        for regra in self.regras:
            try:
                regra(contexto, resultado)
            except Exception as e:
                resultado.alertas.append(f'Erro na regra {regra.__name__}: {str(e)}')
        
        # 4. Persistência do resultado no banco de dados
        self._salvar_resultado(resultado)
        
        return resultado

    def processar_movimento(self, movement_id: int) -> int:
        """
        Processa todos os itens de um movimento fiscal e gera/persiste AuditAlerts
        """
        from src.models.fiscal import FiscalMovement, FiscalMovementItem
        from src.models.audit import AuditAlert
        try:
            from motor_fiscal.auditorias.totais import verificar_totais_nota
        except ImportError:
            verificar_totais_nota = None

        movement = self.session.query(FiscalMovement).filter(FiscalMovement.id == movement_id).first()
        if not movement:
            raise ValueError(f"Movimento {movement_id} nao encontrado")

        try:
            self.session.query(AuditAlert).filter(AuditAlert.movimento_id == movement_id).delete()
            self.session.commit()
        except Exception:
            self.session.rollback()

        items = self.session.query(FiscalMovementItem).filter(FiscalMovementItem.movimento_id == movement_id).all()
        total_alerts = 0

        # Auditoria de Totais (Nível Nota)
        if verificar_totais_nota:
            alertas_totais = verificar_totais_nota(self, movement_id)
            for alt in alertas_totais:
                alert = AuditAlert(
                    empresa_id=movement.empresa_id,
                    movimento_id=movement_id,
                    tipo=alt['tipo'],
                    severidade=alt['severidade'],
                    descricao=alt['descricao'],
                    status='pendente'
                )
                if hasattr(AuditAlert, 'regra_id'):
                    setattr(alert, 'regra_id', alt['regra_id'])
                self.session.add(alert)
                total_alerts += 1

        for item in items:
            resultado = self.processar_item(item.id)
            
            for alerta_dict in resultado.alertas_auditoria:
                alert = AuditAlert(
                    empresa_id=movement.empresa_id,
                    movimento_id=movement_id,
                    tipo=alerta_dict.get('tipo', 'Outro'),
                    severidade=alerta_dict.get('severidade', 'warning'),
                    descricao=alerta_dict.get('descricao', ''),
                    status='pendente'
                )
                if hasattr(AuditAlert, 'item_id'):
                    setattr(alert, 'item_id', item.id)
                elif hasattr(AuditAlert, 'item_movimento_id'):
                    setattr(alert, 'item_movimento_id', item.id)
                if hasattr(AuditAlert, 'regra_id'):
                    setattr(alert, 'regra_id', alerta_dict.get('regra_id', ''))
                
                self.session.add(alert)
                total_alerts += 1

            for alerta_str in resultado.alertas:
                if any(x.get('descricao') == alerta_str for x in resultado.alertas_auditoria):
                    continue
                alert = AuditAlert(
                    empresa_id=movement.empresa_id,
                    movimento_id=movement_id,
                    tipo='Geral',
                    severidade='warning',
                    descricao=alerta_str,
                    status='pendente'
                )
                if hasattr(AuditAlert, 'item_id'):
                    setattr(alert, 'item_id', item.id)
                elif hasattr(AuditAlert, 'item_movimento_id'):
                    setattr(alert, 'item_movimento_id', item.id)
                if hasattr(AuditAlert, 'regra_id'):
                    setattr(alert, 'regra_id', 'geral')

                self.session.add(alert)
                total_alerts += 1

        self.session.commit()
        return total_alerts

    def _salvar_resultado(self, res: ResultadoFiscal):
        """Grava a decisão do motor na tabela motor_fiscal_resultado"""
        # Busca resultado anterior para atualizar ou cria novo
        existente = self.session.query(MotorFiscalResultado).filter(MotorFiscalResultado.item_movimento_id == res.item_id).first()
        
        if existente:
            existing_res = existente
        else:
            existing_res = MotorFiscalResultado(item_movimento_id=res.item_id)
            self.session.add(existing_res)

        existing_res.gera_credito = res.gera_credito
        existing_res.gera_debito = res.gera_debito
        existing_res.monofasico = res.monofasico
        existing_res.substituicao_tributaria = res.substituicao_tributaria
        existing_res.motivo = res.motivo
        
        self.session.commit()