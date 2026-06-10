from motor_fiscal.models.contexto import ContextoFiscal, ResultadoFiscal
from motor_fiscal.auditorias.helpers import aplica_regras_ncm
from src.database.session import get_session
from src.models.ncm_referencia import NcmReferencia

def get_monofasicos_ncms():
    try:
        session = get_session()
        ncms = session.query(NcmReferencia).filter(NcmReferencia.monofasico_pis_cofins == True).all()
        session.close()
        if ncms:
            return [n.codigo for n in ncms]
    except Exception:
        pass
    return ['12345678', '87654321']

def regra_ncm_vazio_ou_invalido(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_ncm(contexto):
        return
    if not contexto.ncm:
        resultado.alertas_auditoria.append({
            'tipo': 'NCM',
            'severidade': 'critical',
            'descricao': 'NCM ausente ou em branco',
            'regra_id': 'ncm_vazio'
        })
    elif len(contexto.ncm) != 8 or not contexto.ncm.isdigit():
        resultado.alertas_auditoria.append({
            'tipo': 'NCM',
            'severidade': 'error',
            'descricao': f'NCM {contexto.ncm} invalido (deve conter 8 digitos numericos)',
            'regra_id': 'ncm_invalido'
        })

def regra_ncm_monofasico_tributacao(contexto: ContextoFiscal, resultado: ResultadoFiscal):
    if not aplica_regras_ncm(contexto):
        return
    monofasicos = get_monofasicos_ncms()
    if contexto.ncm in monofasicos:
        # PIS CST should be '04', '06', '07', etc.
        # If it is '01' (Tributado Aliquota Basica) or similar, it's incorrect.
        if contexto.cst_pis in ['01', '02', '03'] or contexto.cst_cofins in ['01', '02', '03']:
            resultado.alertas_auditoria.append({
                'tipo': 'Tributacao Monofasica',
                'severidade': 'error',
                'descricao': f'Produto com NCM monofasico ({contexto.ncm}) tributado indevidamente (CST PIS={contexto.cst_pis}, COFINS={contexto.cst_cofins})',
                'regra_id': 'ncm_monofasico_tributado_indevidamente'
            })
