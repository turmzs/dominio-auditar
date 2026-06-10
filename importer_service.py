from datetime import datetime
from src.database.session import get_session
from src.models.base import Company, Supplier, Product
from src.models.fiscal import FiscalMovement, FiscalMovementItem, FiscalXml
from src.xml.parsers.registry import parse_xml_document


class FiscalImporter:
    def __init__(self, company_id):
        self.company_id = company_id
        self.session = get_session()

    def import_xml(self, xml_path):
        company = self.session.query(Company).filter(Company.id == self.company_id).first()
        if not company:
            return {'status': 'error', 'message': 'Empresa nao encontrada'}

        try:
            doc = parse_xml_document(xml_path, company_cnpj=company.cnpj)
        except ValueError as exc:
            return {'status': 'error', 'message': str(exc)}
        if not doc:
            return {'status': 'error', 'message': 'Falha ao analisar XML'}

        parsed = doc.to_dict()
        access_key = parsed.get('access_key', '')
        doc_tipo = (parsed.get('doc_tipo') or 'nfe').upper()

        if not parsed.get('itens'):
            return {
                'status': 'error',
                'message': f'Nenhum item/linha extraido do documento ({doc_tipo}).',
            }

        if not parsed.get('numero'):
            return {'status': 'error', 'message': 'Numero do documento nao identificado no XML.'}

        existing = self._find_existing(access_key, parsed, doc_tipo)
        if existing:
            return {
                'status': 'success',
                'movement_id': existing.id,
                'duplicate': True,
                'doc_tipo': doc_tipo,
                'message': f'{doc_tipo} ja importado. Exibindo auditoria do movimento existente.',
            }

        try:
            supplier = None
            if parsed['tipo'] == 'entrada':
                cnpj_emit = parsed['emitente_cnpj']
                supplier = self.session.query(Supplier).filter(Supplier.cnpj == cnpj_emit).first()
                if not supplier:
                    supplier = Supplier(
                        empresa_id=self.company_id,
                        cnpj=cnpj_emit,
                        razao_social=parsed['emitente_nome'],
                    )
                    self.session.add(supplier)
                    self.session.flush()

            try:
                data_emissao = datetime.strptime(parsed.get('data_emissao', ''), '%Y-%m-%d').date()
            except Exception:
                data_emissao = datetime.utcnow().date()

            movement = FiscalMovement(
                empresa_id=self.company_id,
                chave_nfe=access_key or None,
                numero_nota=str(parsed['numero']),
                serie=parsed.get('serie') or None,
                tipo_documento=doc_tipo,
                tipo_movimento=parsed['tipo'].upper(),
                data_emissao=data_emissao,
                fornecedor_id=supplier.id if supplier else None,
                valor_total=parsed.get('valor_total', 0),
                valor_produtos=parsed.get('valor_produtos', 0),
                valor_icms=parsed.get('valor_icms', 0),
                valor_ipi=parsed.get('valor_ipi', 0),
                valor_pis=parsed.get('valor_pis', 0),
                valor_cofins=parsed.get('valor_cofins', 0),
            )

            self.session.add(movement)
            self.session.flush()

            for item_data in parsed.get('itens', []):
                self._add_item(movement.id, item_data, doc_tipo)

            xml_rec = FiscalXml(
                empresa_id=self.company_id,
                chave_nfe=access_key,
                caminho_arquivo=xml_path,
                processado=True,
            )
            self.session.add(xml_rec)
            self.session.commit()
            return {
                'status': 'success',
                'movement_id': movement.id,
                'doc_tipo': doc_tipo,
            }
        except Exception as e:
            self.session.rollback()
            return {'status': 'error', 'message': str(e)}
        finally:
            self.session.close()

    def _find_existing(self, access_key, parsed, doc_tipo):
        if access_key:
            found = self.session.query(FiscalMovement).filter(
                FiscalMovement.chave_nfe == access_key
            ).first()
            if found:
                return found
        return self.session.query(FiscalMovement).filter(
            FiscalMovement.empresa_id == self.company_id,
            FiscalMovement.numero_nota == str(parsed['numero']),
            FiscalMovement.tipo_documento == doc_tipo,
        ).first()

    def _add_item(self, movement_id, item_data, doc_tipo):
        ncm = item_data.get('ncm') or ''
        cod_serv = item_data.get('codigo_servico') or ''
        is_servico = doc_tipo == 'NFSE'
        product_key = cod_serv if is_servico else (ncm or cod_serv or f'{doc_tipo}_ITEM')
        ncm_db = None if is_servico else (ncm or None)
        codigo_item = cod_serv if is_servico else ncm_db

        product = self.session.query(Product).filter(
            Product.company_id == self.company_id,
            Product.codigo == f'AUTO_{product_key}',
        ).first()
        if not product:
            product = Product(
                company_id=self.company_id,
                descricao=item_data.get('descricao') or f'Item {doc_tipo}',
                ncm=ncm_db,
                codigo=f'AUTO_{product_key}',
            )
            self.session.add(product)
            self.session.flush()

        f_item = FiscalMovementItem(
            movimento_id=movement_id,
            produto_id=product.id,
            descricao=item_data.get('descricao', ''),
            cfop=item_data.get('cfop', ''),
            cst_icms=item_data.get('cst_icms', ''),
            csosn=item_data.get('csosn', ''),
            cst_pis=item_data.get('cst_pis', ''),
            cst_cofins=item_data.get('cst_cofins', ''),
            cst_ipi=item_data.get('cst_ipi', ''),
            base_ipi=item_data.get('base_ipi', 0.0),
            valor_ipi=item_data.get('valor_ipi', 0.0),
            ncm=codigo_item,
            quantidade=item_data.get('quantidade', 1),
            valor_unitario=item_data.get('valor_unitario', 0),
            valor_total=item_data.get('valor_total', 0),
            base_icms=item_data.get('base_icms', 0),
            valor_icms=item_data.get('valor_icms', 0),
            base_pis=item_data.get('base_pis', 0),
            valor_pis=item_data.get('valor_iss', 0) if is_servico else item_data.get('valor_pis', 0),
            base_cofins=item_data.get('base_cofins', 0),
            valor_cofins=item_data.get('valor_cofins', 0),
        )
        self.session.add(f_item)
