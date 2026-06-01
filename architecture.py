"""
ESCRITA_FISCAL_V1 - Arquitetura Funcional do Sistema
Define a estrutura hierárquica de todos os módulos do sistema
"""

ARCHITECTURE = {
    "CORE": {
        "label": "CORE",
        "description": "Núcleo do sistema",
        "etapa": 1,
        "modules": [
            {"id": "autenticacao", "label": "Autenticação", "route": "/core/autenticacao"},
            {"id": "permissoes", "label": "Permissões", "route": "/core/permissoes"},
            {"id": "empresas", "label": "Empresas", "route": "/core/empresas"},
            {"id": "filiais", "label": "Filiais", "route": "/core/filiais"},
            {"id": "usuarios", "label": "Usuários", "route": "/core/usuarios"},
            {"id": "logs", "label": "Logs", "route": "/core/logs"},
            {"id": "auditoria", "label": "Auditoria", "route": "/core/auditoria"},
            {"id": "configuracoes_gerais", "label": "Configurações Gerais", "route": "/core/configuracoes"},
        ]
    },
    
    "CONTROLE": {
        "label": "Controle",
        "description": "Controle de parâmetros e configurações",
        "etapa": 1,
        "modules": [
            {"id": "empresas_controle", "label": "Empresas", "route": "/controle/empresas"},
            {
                "id": "parametros", 
                "label": "Parâmetros",
                "route": "/controle/parametros",
                "submodules": [
                    {"id": "param_geral", "label": "Geral", "route": "/controle/parametros/geral"},
                    {"id": "param_federal", "label": "Federal", "route": "/controle/parametros/federal"},
                    {"id": "param_estadual", "label": "Estadual", "route": "/controle/parametros/estadual"},
                    {"id": "param_municipal", "label": "Municipal", "route": "/controle/parametros/municipal"},
                    {"id": "param_cfop", "label": "CFOP", "route": "/controle/parametros/cfop"},
                    {"id": "param_cfps", "label": "CFPS", "route": "/controle/parametros/cfps"},
                    {"id": "param_contabilidade", "label": "Contabilidade", "route": "/controle/parametros/contabilidade"},
                    {"id": "param_impostos", "label": "Impostos", "route": "/controle/parametros/impostos"},
                    {"id": "param_sped", "label": "SPED", "route": "/controle/parametros/sped"},
                    {"id": "param_sintegra", "label": "Sintegra", "route": "/controle/parametros/sintegra"},
                ]
            },
            {"id": "impostos_controle", "label": "Impostos", "route": "/controle/impostos"},
            {"id": "tabelas_controle", "label": "Tabelas", "route": "/controle/tabelas"},
            {"id": "rotinas_automaticas", "label": "Rotinas Automáticas", "route": "/controle/rotinas"},
            {"id": "responsaveis_controle", "label": "Responsáveis", "route": "/controle/responsaveis"},
            {"id": "administradora_cartoes", "label": "Administradora de Cartões", "route": "/controle/cartoes"},
        ]
    },

    "ARQUIVOS": {
        "label": "Arquivos",
        "description": "Cadastros mestres",
        "etapa": 2,
        "modules": [
            {"id": "clientes", "label": "Clientes", "route": "/arquivos/clientes"},
            {"id": "fornecedores", "label": "Fornecedores", "route": "/arquivos/fornecedores"},
            {"id": "produtos", "label": "Produtos", "route": "/arquivos/produtos"},
            {"id": "servicos", "label": "Serviços", "route": "/arquivos/servicos"},
            {"id": "grupos", "label": "Grupos", "route": "/arquivos/grupos"},
            {"id": "unidades", "label": "Unidades", "route": "/arquivos/unidades"},
            {"id": "acumuladores", "label": "Acumuladores", "route": "/arquivos/acumuladores"},
            {"id": "historicos", "label": "Históricos", "route": "/arquivos/historicos"},
            {"id": "contas", "label": "Contas", "route": "/arquivos/contas"},
            {"id": "impostos_arquivos", "label": "Impostos", "route": "/arquivos/impostos"},
            {"id": "ajustes", "label": "Ajustes", "route": "/arquivos/ajustes"},
            {"id": "observacoes", "label": "Observações", "route": "/arquivos/observacoes"},
            {"id": "info_complementares", "label": "Informações Complementares", "route": "/arquivos/info_complementares"},
            {"id": "responsaveis_arquivos", "label": "Responsáveis", "route": "/arquivos/responsaveis"},
            {"id": "ncm_cest_nbs", "label": "Dados NCM/CEST/NBS", "route": "/arquivos/ncm"},
            {"id": "config_importacao", "label": "Configuração de Importação", "route": "/arquivos/config_importacao"},
        ]
    },

    "XML": {
        "label": "XML",
        "description": "Processamento de documentos eletrônicos",
        "etapa": 3,
        "modules": [
            {
                "id": "nfe",
                "label": "NF-e",
                "route": "/xml/nfe",
                "submodules": [
                    {"id": "nfe_portal", "label": "Portal", "route": "/xml/nfe/portal"},
                    {"id": "nfe_xml", "label": "XML", "route": "/xml/nfe/xml"},
                    {"id": "nfe_api", "label": "API", "route": "/xml/nfe/api"},
                    {"id": "nfe_manifestacao", "label": "Manifestação", "route": "/xml/nfe/manifestacao"},
                ]
            },
            {"id": "nfce", "label": "NFC-e", "route": "/xml/nfce"},
            {"id": "nfse", "label": "NFS-e", "route": "/xml/nfse"},
            {"id": "cte", "label": "CT-e", "route": "/xml/cte"},
            {"id": "cte_os", "label": "CT-e OS", "route": "/xml/cte_os"},
            {"id": "nfcom", "label": "NFCom", "route": "/xml/nfcom"},
            {"id": "nf3e", "label": "NF3-e", "route": "/xml/nf3e"},
            {"id": "cupom_fiscal", "label": "Cupom Fiscal", "route": "/xml/cupom"},
            {"id": "sped_fiscal_xml", "label": "SPED Fiscal", "route": "/xml/sped_fiscal"},
            {"id": "sped_contrib_xml", "label": "SPED Contribuições", "route": "/xml/sped_contrib"},
            {"id": "sintegra_xml", "label": "Sintegra", "route": "/xml/sintegra"},
            {"id": "convenio_115_xml", "label": "Convênio 115", "route": "/xml/convenio_115"},
            {"id": "onbalance_xml", "label": "OnBalance", "route": "/xml/onbalance"},
            {"id": "auditoria_xml", "label": "Auditoria XML", "route": "/xml/auditoria"},
        ]
    },

    "MOVIMENTOS": {
        "label": "Movimentos",
        "description": "Movimentações fiscais",
        "etapa": 4,
        "modules": [
            {"id": "entradas", "label": "Entradas", "route": "/movimentos/entradas"},
            {"id": "saidas", "label": "Saídas", "route": "/movimentos/saidas"},
            {"id": "servicos", "label": "Serviços", "route": "/movimentos/servicos"},
            {"id": "reducoes_z", "label": "Reduções Z", "route": "/movimentos/reducoes_z"},
            {"id": "estoque", "label": "Estoque", "route": "/movimentos/estoque"},
            {"id": "baixas", "label": "Baixas", "route": "/movimentos/baixas"},
            {"id": "parcelamentos", "label": "Parcelamentos", "route": "/movimentos/parcelamentos"},
            {"id": "pagamentos", "label": "Pagamentos", "route": "/movimentos/pagamentos"},
            {"id": "integracao_contabil", "label": "Integração Contábil", "route": "/movimentos/integracao"},
            {"id": "apuracao_movimentos", "label": "Apuração", "route": "/movimentos/apuracao"},
        ]
    },

    "MOTOR_FISCAL": {
        "label": "Motor Fiscal",
        "description": "Cálculo de tributos",
        "etapa": 6,
        "modules": [
            {"id": "icms", "label": "ICMS", "route": "/motor/icms"},
            {"id": "icms_st", "label": "ICMS ST", "route": "/motor/icms_st"},
            {"id": "difal", "label": "DIFAL", "route": "/motor/difal"},
            {"id": "fcp", "label": "FCP", "route": "/motor/fcp"},
            {"id": "ipi", "label": "IPI", "route": "/motor/ipi"},
            {"id": "pis", "label": "PIS", "route": "/motor/pis"},
            {"id": "cofins", "label": "COFINS", "route": "/motor/cofins"},
            {"id": "iss", "label": "ISS", "route": "/motor/iss"},
            {"id": "inss", "label": "INSS", "route": "/motor/inss"},
            {"id": "irrf", "label": "IRRF", "route": "/motor/irrf"},
            {"id": "csll", "label": "CSLL", "route": "/motor/csll"},
            {"id": "simples_nacional_motor", "label": "Simples Nacional", "route": "/motor/simples"},
            {"id": "lucro_presumido_motor", "label": "Lucro Presumido", "route": "/motor/presumido"},
            {"id": "lucro_real_motor", "label": "Lucro Real", "route": "/motor/real"},
            {"id": "retencoes", "label": "Retenções", "route": "/motor/retencoes"},
            {"id": "creditos", "label": "Créditos", "route": "/motor/creditos"},
            {"id": "ressarcimentos", "label": "Ressarcimentos", "route": "/motor/ressarcimentos"},
            {"id": "beneficios_fiscais", "label": "Benefícios Fiscais", "route": "/motor/beneficios"},
        ]
    },

    "APURACAO": {
        "label": "Apuração",
        "description": "Apuração de tributos",
        "etapa": 7,
        "modules": [
            {"id": "apuracao_simples", "label": "Simples Nacional", "route": "/apuracao/simples"},
            {"id": "apuracao_presumido", "label": "Lucro Presumido", "route": "/apuracao/presumido"},
            {"id": "apuracao_real", "label": "Lucro Real", "route": "/apuracao/real"},
            {"id": "apuracao_icms", "label": "ICMS", "route": "/apuracao/icms"},
            {"id": "apuracao_icms_st", "label": "ICMS ST", "route": "/apuracao/icms_st"},
            {"id": "apuracao_pis", "label": "PIS", "route": "/apuracao/pis"},
            {"id": "apuracao_cofins", "label": "COFINS", "route": "/apuracao/cofins"},
            {"id": "apuracao_iss", "label": "ISS", "route": "/apuracao/iss"},
            {"id": "apuracao_federais", "label": "Federais", "route": "/apuracao/federais"},
            {"id": "parcelamentos_apuracao", "label": "Parcelamentos", "route": "/apuracao/parcelamentos"},
            {"id": "conferencias", "label": "Conferências", "route": "/apuracao/conferencias"},
        ]
    },

    "RELATORIOS": {
        "label": "Relatórios",
        "description": "Geração de relatórios",
        "etapa": 5,
        "modules": [
            {"id": "livros", "label": "Livros", "route": "/relatorios/livros"},
            {"id": "guias_rel", "label": "Guias", "route": "/relatorios/guias"},
            {"id": "informativos", "label": "Informativos", "route": "/relatorios/informativos"},
            {"id": "impostos_rel", "label": "Impostos", "route": "/relatorios/impostos"},
            {
                "id": "acompanhamentos",
                "label": "Acompanhamentos",
                "route": "/relatorios/acompanhamentos",
                "submodules": [
                    {"id": "acomp_entradas", "label": "Entradas", "route": "/relatorios/acomp/entradas"},
                    {"id": "acomp_saidas", "label": "Saídas", "route": "/relatorios/acomp/saidas"},
                    {"id": "acomp_servicos", "label": "Serviços", "route": "/relatorios/acomp/servicos"},
                    {"id": "acomp_cte", "label": "CT-e", "route": "/relatorios/acomp/cte"},
                    {"id": "acomp_cupons", "label": "Cupons", "route": "/relatorios/acomp/cupons"},
                    {"id": "acomp_faturamento", "label": "Faturamento", "route": "/relatorios/acomp/faturamento"},
                    {"id": "acomp_cfop", "label": "CFOP e Alíquota", "route": "/relatorios/acomp/cfop"},
                    {"id": "acomp_interestaduais", "label": "Interestaduais", "route": "/relatorios/acomp/interestaduais"},
                    {"id": "acomp_inconsistencias", "label": "Inconsistências", "route": "/relatorios/acomp/inconsistencias"},
                ]
            },
            {"id": "estoque_rel", "label": "Estoque", "route": "/relatorios/estoque"},
            {"id": "cadastrais", "label": "Cadastrais", "route": "/relatorios/cadastrais"},
            {"id": "financeiros", "label": "Financeiros", "route": "/relatorios/financeiros"},
            {"id": "gerenciador_relatorios", "label": "Gerenciador de Relatórios", "route": "/relatorios/gerenciador"},
        ]
    },

    "OBRIGACOES_ACESSORIAS": {
        "label": "Obrigações Acessórias",
        "description": "Declarações e obrigações",
        "etapa": 8,
        "modules": [
            {"id": "sped_fiscal", "label": "SPED Fiscal", "route": "/obrigacoes/sped_fiscal"},
            {"id": "sped_contrib", "label": "SPED Contribuições", "route": "/obrigacoes/sped_contrib"},
            {"id": "efd_reinf", "label": "EFD-Reinf", "route": "/obrigacoes/efd_reinf"},
            {"id": "dctfweb", "label": "DCTFWeb", "route": "/obrigacoes/dctfweb"},
            {"id": "sintegra", "label": "Sintegra", "route": "/obrigacoes/sintegra"},
            {"id": "destda", "label": "DeSTDA", "route": "/obrigacoes/destda"},
            {"id": "gia", "label": "GIA", "route": "/obrigacoes/gia"},
            {"id": "gia_st", "label": "GIA-ST", "route": "/obrigacoes/gia_st"},
            {"id": "dimob", "label": "DIMOB", "route": "/obrigacoes/dimob"},
            {"id": "dirf", "label": "DIRF (histórico)", "route": "/obrigacoes/dirf"},
            {"id": "obrigacoes_estaduais", "label": "Obrigações Estaduais", "route": "/obrigacoes/estaduais"},
        ]
    },

    "GUIAS": {
        "label": "Guias",
        "description": "Geração de guias de pagamento",
        "etapa": 7,
        "modules": [
            {"id": "das", "label": "DAS", "route": "/guias/das"},
            {"id": "darf", "label": "DARF", "route": "/guias/darf"},
            {"id": "icms_guia", "label": "ICMS", "route": "/guias/icms"},
            {"id": "iss_guia", "label": "ISS", "route": "/guias/iss"},
            {"id": "gnre", "label": "GNRE", "route": "/guias/gnre"},
            {"id": "gare", "label": "GARE", "route": "/guias/gare"},
            {"id": "dae", "label": "DAE", "route": "/guias/dae"},
            {"id": "outras_guias", "label": "Outras Guias", "route": "/guias/outras"},
        ]
    },

    "UTILITARIOS": {
        "label": "Utilitários",
        "description": "Funções auxiliares",
        "etapa": 5,
        "modules": [
            {"id": "dashboard_gerencial", "label": "Dashboard Gerencial", "route": "/utilitarios/dashboard"},
            {"id": "consulta", "label": "Consulta", "route": "/utilitarios/consulta"},
            {"id": "backup", "label": "Backup", "route": "/utilitarios/backup"},
            {"id": "importacao", "label": "Importação", "route": "/utilitarios/importacao"},
            {"id": "exportacao", "label": "Exportação", "route": "/utilitarios/exportacao"},
            {"id": "regeracao", "label": "Regeração", "route": "/utilitarios/regeracao"},
            {"id": "alteracoes_em_massa", "label": "Alterações em Massa", "route": "/utilitarios/alteracoes_massa"},
            {"id": "conversoes", "label": "Conversões", "route": "/utilitarios/conversoes"},
            {"id": "auditoria_utils", "label": "Auditoria", "route": "/utilitarios/auditoria"},
            {"id": "recursos_maquina", "label": "Recursos da Máquina", "route": "/utilitarios/recursos"},
            {"id": "favoritos", "label": "Favoritos", "route": "/utilitarios/favoritos"},
        ]
    },

    "INTEGRACOES": {
        "label": "Integrações",
        "description": "Integrações externas",
        "etapa": 8,
        "modules": [
            {"id": "receita_federal", "label": "Receita Federal", "route": "/integracoes/rf"},
            {"id": "sefaz", "label": "SEFAZ", "route": "/integracoes/sefaz"},
            {"id": "portal_nfse", "label": "Portal Nacional NFS-e", "route": "/integracoes/nfse"},
            {"id": "ecac", "label": "e-CAC", "route": "/integracoes/ecac"},
            {"id": "conta_azul", "label": "Conta Azul", "route": "/integracoes/conta_azul"},
            {"id": "onvio", "label": "Onvio", "route": "/integracoes/onvio"},
            {"id": "kolossus", "label": "Kolossus", "route": "/integracoes/kolossus"},
            {"id": "apis_internas", "label": "APIs Internas", "route": "/integracoes/apis"},
        ]
    },

    "AJUDA": {
        "label": "Ajuda",
        "description": "Documentação e suporte",
        "etapa": None,
        "modules": [
            {"id": "manual", "label": "Manual", "route": "/ajuda/manual"},
            {"id": "treinamentos", "label": "Treinamentos", "route": "/ajuda/treinamentos"},
            {"id": "atualizacoes", "label": "Atualizações", "route": "/ajuda/atualizacoes"},
            {"id": "base_conhecimento", "label": "Base de Conhecimento", "route": "/ajuda/conhecimento"},
            {"id": "sobre", "label": "Sobre", "route": "/ajuda/sobre"},
        ]
    }
}

# Ordem de implementação por etapas
IMPLEMENTATION_PHASES = [
    {
        "etapa": 1,
        "nome": "Fundação",
        "descricao": "Login, Empresas, Usuários, Permissões",
        "modulos": ["CORE", "CONTROLE (Empresas apenas)"]
    },
    {
        "etapa": 2,
        "nome": "Cadastros Mestres",
        "descricao": "Clientes, Fornecedores, Produtos, NCM, CFOP",
        "modulos": ["ARQUIVOS"]
    },
    {
        "etapa": 3,
        "nome": "Importação XML",
        "descricao": "NF-e, NFS-e, CT-e, Cupom Fiscal",
        "modulos": ["XML"]
    },
    {
        "etapa": 4,
        "nome": "Movimentos",
        "descricao": "Entradas, Saídas, Serviços",
        "modulos": ["MOVIMENTOS"]
    },
    {
        "etapa": 5,
        "nome": "Relatórios e Utilitários",
        "descricao": "Relatórios Zebra, Dashboard, Consultas",
        "modulos": ["RELATORIOS", "UTILITARIOS"]
    },
    {
        "etapa": 6,
        "nome": "Motor Fiscal",
        "descricao": "Cálculo de ICMS, IPI, PIS, COFINS",
        "modulos": ["MOTOR_FISCAL"]
    },
    {
        "etapa": 7,
        "nome": "Apuração e Guias",
        "descricao": "Apuração de tributos, Geração de Guias",
        "modulos": ["APURACAO", "GUIAS"]
    },
    {
        "etapa": 8,
        "nome": "Compliance",
        "descricao": "SPED, EFD-Reinf, Integrações",
        "modulos": ["OBRIGACOES_ACESSORIAS", "INTEGRACOES"]
    }
]


def get_menu_structure():
    """Retorna a estrutura de menu em cascata"""
    menu = []
    for key, module in ARCHITECTURE.items():
        menu_item = {
            "id": key.lower(),
            "label": module["label"],
            "route": f"/{key.lower()}",
            "etapa": module["etapa"],
        }
        
        if "modules" in module:
            menu_item["submenus"] = []
            for submodule in module["modules"]:
                submenu = {
                    "id": submodule["id"],
                    "label": submodule["label"],
                    "route": submodule["route"],
                }
                
                if "submodules" in submodule:
                    submenu["items"] = [
                        {
                            "id": item["id"],
                            "label": item["label"],
                            "route": item["route"],
                        }
                        for item in submodule["submodules"]
                    ]
                
                menu_item["submenus"].append(submenu)
        
        menu.append(menu_item)
    
    return menu
