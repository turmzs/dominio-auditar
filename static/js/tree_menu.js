/* ============================================
   TREE MENU CONTROLLER - DOMINIO ESCRITA FISCAL
   ============================================ */

// Menu structure
const menuStructure = [
    {
        label: 'Controle',
        icon: 'fa-sliders-h',
        children: [
            {
                label: 'Empresas',
                children: [
                    { label: 'Cadastro', id: 'empresas-cadastro' },
                    { label: 'Dados Gerais', id: 'empresas-gerais' },
                    { label: 'Responsáveis', id: 'empresas-responsaveis' },
                    { label: 'Atividades', id: 'empresas-atividades' },
                    { label: 'Registros', id: 'empresas-registros' },
                    { label: 'Configurações', id: 'empresas-config' }
                ]
            },
            {
                label: 'Parâmetros',
                children: [
                    { label: 'Geral', id: 'parametros-geral' },
                    { label: 'Federal', id: 'parametros-federal' },
                    { label: 'Estadual', id: 'parametros-estadual' },
                    { label: 'Estadual II', id: 'parametros-estadual2' },
                    { label: 'Municipais', id: 'parametros-municipais' },
                    { label: 'CFOP', id: 'parametros-cfop' },
                    { label: 'CFPS', id: 'parametros-cfps' },
                    { label: 'Contabilidade', id: 'parametros-contab' },
                    { label: 'Impostos', id: 'parametros-impostos' },
                    { label: 'Ajustes', id: 'parametros-ajustes' },
                    { label: 'Observações', id: 'parametros-obs' },
                    { label: 'SPED Fiscal', id: 'parametros-sped' },
                    { label: 'SPED PIS/COFINS', id: 'parametros-sped-pis' },
                    { label: 'Sintegra', id: 'parametros-sintegra' },
                    { label: 'Convênio 115', id: 'parametros-convenio' }
                ]
            },
            { label: 'Impostos', id: 'controle-impostos' },
            { label: 'Tabelas', id: 'controle-tabelas' },
            { label: 'Tabelas Crédito Presumido', id: 'controle-credito' },
            { label: 'Rotinas Automáticas', id: 'controle-rotinas' },
            { label: 'Dados Reduções Z', id: 'controle-reducoes' },
            { label: 'Responsáveis', id: 'controle-responsaveis' },
            { label: 'Administradora de Cartões', id: 'controle-cartoes' }
        ]
    },
    {
        label: 'Arquivos',
        icon: 'fa-folder',
        children: [
            { label: 'Fornecedores', id: 'arquivos-fornecedores' },
            { label: 'Clientes', id: 'arquivos-clientes' },
            { label: 'Remetentes/Destinatários', id: 'arquivos-remetentes' },
            { label: 'Operadora Plano Saúde', id: 'arquivos-operadora' },
            { label: 'Grupos', id: 'arquivos-grupos' },
            { label: 'Produtos', id: 'arquivos-produtos' },
            { label: 'Dados Impostos NCM/CEST/NBS', id: 'arquivos-ncm' },
            { label: 'Unidades', id: 'arquivos-unidades' },
            { label: 'Contas', id: 'arquivos-contas' },
            { label: 'Históricos', id: 'arquivos-historicos' },
            { label: 'Configuração Históricos', id: 'arquivos-config-hist' },
            { label: 'Acumuladores', id: 'arquivos-acumuladores' },
            { label: 'Impostos', id: 'arquivos-impostos' },
            { label: 'Ajustes', id: 'arquivos-ajustes' },
            { label: 'Observações', id: 'arquivos-obs' },
            { label: 'Informações Complementares', id: 'arquivos-info-comp' },
            {
                label: 'Configuração Importação',
                children: [
                    { label: 'NF-e Portal', id: 'importacao-nfe-portal' },
                    { label: 'NF-e XML', id: 'importacao-nfe' },
                    { label: 'NFC-e XML', id: 'importacao-nfce' },
                    { label: 'NFS-e XML', id: 'importacao-nfse' },
                    { label: 'CT-e XML', id: 'importacao-cte' },
                    { label: 'NFCom XML', id: 'importacao-nfcom' },
                    { label: 'NF3-e XML', id: 'importacao-nf3e' },
                    { label: 'SPED Fiscal', id: 'importacao-sped' },
                    { label: 'SPED PIS/COFINS', id: 'importacao-sped-pis' },
                    { label: 'Sintegra', id: 'importacao-sintegra' },
                    { label: 'Convênio 115', id: 'importacao-convenio' },
                    { label: 'OnBalance', id: 'importacao-onbalance' },
                    { label: 'Kolossus', id: 'importacao-kolossus' }
                ]
            },
            { label: 'Tabelas', id: 'arquivos-tabelas' },
            { label: 'Crédito Presumido', id: 'arquivos-credito' },
            { label: 'Rotinas Automáticas', id: 'arquivos-rotinas' },
            { label: 'Reduções Z', id: 'arquivos-reducoes' },
            { label: 'Responsáveis', id: 'arquivos-responsaveis' }
        ]
    },
    {
        label: 'Movimentos',
        icon: 'fa-exchange-alt',
        children: [
            {
                label: 'Entradas',
                children: [
                    { label: 'Geral', id: 'entradas-geral' },
                    { label: 'Complementar', id: 'entradas-compl' },
                    { label: 'Estadual', id: 'entradas-estadual' },
                    { label: 'Estoque', id: 'entradas-estoque' },
                    { label: 'ICMS', id: 'entradas-icms' },
                    { label: 'SPED', id: 'entradas-sped' },
                    { label: 'Parcelas', id: 'entradas-parcelas' },
                    { label: 'Contabilidade', id: 'entradas-contab' },
                    { label: 'Municipais', id: 'entradas-municipais' }
                ]
            },
            {
                label: 'Saídas',
                children: [
                    { label: 'Geral', id: 'saidas-geral' },
                    { label: 'Complementar', id: 'saidas-compl' },
                    { label: 'Estadual', id: 'saidas-estadual' },
                    { label: 'Exportação', id: 'saidas-exportacao' },
                    { label: 'Estoque', id: 'saidas-estoque' },
                    { label: 'ICMS', id: 'saidas-icms' },
                    { label: 'SPED', id: 'saidas-sped' },
                    { label: 'Parcelas', id: 'saidas-parcelas' },
                    { label: 'Contabilidade', id: 'saidas-contab' }
                ]
            },
            { label: 'Serviços', id: 'movimentos-servicos' },
            { label: 'Reduções Z', id: 'movimentos-reducoes' },
            {
                label: 'Estoque',
                children: [
                    { label: 'Impostos Lançados', id: 'estoque-lancados' },
                    { label: 'Impostos Calculados', id: 'estoque-calculados' },
                    { label: 'Ajustes PIS/COFINS', id: 'estoque-ajustes' },
                    { label: 'Créditos PIS/COFINS', id: 'estoque-creditos' },
                    { label: 'Simples Nacional', id: 'estoque-simples' },
                    { label: 'AIDF', id: 'estoque-aidf' },
                    { label: 'Termos Ocorrência', id: 'estoque-termos' },
                    { label: 'Retenções IRRF', id: 'estoque-irrf' }
                ]
            },
            { label: 'Baixas', id: 'movimentos-baixas' },
            { label: 'Apuração', id: 'movimentos-apuracao' },
            { label: 'Apuração Tributos Federais', id: 'movimentos-apuracao-fed' },
            { label: 'Parcelamento Impostos', id: 'movimentos-parcelamento' },
            { label: 'Parcelamento Simples', id: 'movimentos-parcelamento-simples' },
            { label: 'Pagamento Impostos', id: 'movimentos-pagamento' },
            { label: 'Pagamento via e-CAC', id: 'movimentos-pagamento-ecac' },
            { label: 'Integração Contábil', id: 'movimentos-integracao' },
            { label: 'Rotinas Automáticas', id: 'movimentos-rotinas' },
            { label: 'Conta Azul', id: 'movimentos-azul' }
        ]
    },
    {
        label: 'Relatórios',
        icon: 'fa-chart-bar',
        children: [
            { label: 'Livros', id: 'relatorios-livros' },
            { label: 'Informativos', id: 'relatorios-informativos' },
            { label: 'Guias', id: 'relatorios-guias' },
            { label: 'Impostos', id: 'relatorios-impostos' },
            {
                label: 'Acompanhamentos',
                children: [
                    { label: 'Entradas', id: 'acomp-entradas' },
                    { label: 'Saídas', id: 'acomp-saidas' },
                    { label: 'Serviços', id: 'acomp-servicos' },
                    { label: 'Cupons', id: 'acomp-cupons' },
                    { label: 'CT-e', id: 'acomp-cte' },
                    { label: 'ECF', id: 'acomp-ecf' },
                    { label: 'Demonstrativo Mensal', id: 'acomp-demonstrativo' },
                    { label: 'Faturamento', id: 'acomp-faturamento' },
                    { label: 'CFOP e Alíquota', id: 'acomp-cfop' },
                    { label: 'Interestaduais', id: 'acomp-interestaduais' },
                    { label: 'NF-es', id: 'acomp-nfes' },
                    { label: 'Contas Receber', id: 'acomp-contas' },
                    { label: 'Crédito Presumido', id: 'acomp-credito' },
                    { label: 'Inconsistências', id: 'acomp-inconsistencias' }
                ]
            },
            { label: 'Estoque', id: 'relatorios-estoque' },
            { label: 'Cadastrais', id: 'relatorios-cadastrais' },
            { label: 'Contas Pagar/Receber', id: 'relatorios-contas' },
            { label: 'Gerenciador Relatórios', id: 'relatorios-gerenciador' }
        ]
    },
    {
        label: 'Utilitários',
        icon: 'fa-toolbox',
        children: [
            { label: 'Dashboard Gerencial', id: 'utilitarios-dashboard' },
            {
                label: 'Consulta',
                children: [
                    { label: 'Gráficos', id: 'consulta-graficos' },
                    { label: 'Dashboards', id: 'consulta-dashboards' },
                    { label: 'Empresas', id: 'consulta-empresas' },
                    { label: 'Emitir', id: 'consulta-emitir' }
                ]
            },
            { label: 'Onvio Messenger', id: 'utilitarios-onvio' },
            { label: 'Reforma Tributária', id: 'utilitarios-reforma' },
            { label: 'Backup', id: 'utilitarios-backup' },
            { label: 'Consulta Apuração', id: 'utilitarios-apuracao' },
            {
                label: 'Alterações em Massa',
                children: [
                    { label: 'Produtos', id: 'massa-produtos' },
                    { label: 'Clientes', id: 'massa-clientes' },
                    { label: 'Fornecedores', id: 'massa-fornecedores' },
                    { label: 'Notas', id: 'massa-notas' },
                    { label: 'Impostos', id: 'massa-impostos' },
                    { label: 'Acumuladores', id: 'massa-acumuladores' }
                ]
            },
            { label: 'Parcelas', id: 'utilitarios-parcelas' },
            { label: 'Agrupar SPED', id: 'utilitarios-sped' },
            { label: 'Recursos Máquina', id: 'utilitarios-recursos' },
            { label: 'Importação', id: 'utilitarios-importacao' },
            { label: 'Exportação', id: 'utilitarios-exportacao' },
            { label: 'Kolossus', id: 'utilitarios-kolossus' },
            { label: 'Conversão Municípios', id: 'utilitarios-conversao' },
            { label: 'Regenerar', id: 'utilitarios-regenerar' }
        ]
    },
    { label: 'Favoritos', id: 'favoritos', icon: 'fa-star' },
    { label: 'Ajuda', id: 'ajuda', icon: 'fa-question-circle' }
];

/**
 * Build tree menu
 */
function buildTreeMenu() {
    const treeContainer = document.getElementById('menu-tree');
    treeContainer.innerHTML = '';

    menuStructure.forEach((section, index) => {
        if (section.children) {
            treeContainer.appendChild(createTreeBranch(section));
        } else {
            treeContainer.appendChild(createTreeItem(section));
        }
    });
}

/**
 * Create tree branch (with children)
 */
function createTreeBranch(node, level = 0) {
    const nodeDiv = document.createElement('div');
    nodeDiv.className = 'tree-node';

    if (level === 0) {
        nodeDiv.innerHTML = `<div class="tree-section">${node.label}</div>`;
    }

    // Create expandable container
    const container = document.createElement('div');
    container.className = 'tree-children';

    node.children.forEach(child => {
        if (child.children) {
            container.appendChild(createTreeBranch(child, level + 1));
        } else {
            container.appendChild(createTreeItem(child, level + 1));
        }
    });

    if (level > 0) {
        // Create item with toggle
        const itemDiv = document.createElement('div');
        itemDiv.className = 'tree-item';
        itemDiv.onclick = (e) => {
            e.stopPropagation();
            toggleNode(container, toggle);
        };

        const toggle = document.createElement('span');
        toggle.className = 'tree-toggle';
        toggle.innerHTML = '<i class="fas fa-chevron-down"></i>';

        itemDiv.appendChild(toggle);
        itemDiv.appendChild(document.createTextNode(node.label));

        nodeDiv.appendChild(itemDiv);
    }

    nodeDiv.appendChild(container);
    return nodeDiv;
}

/**
 * Create tree leaf item
 */
function createTreeItem(node, level = 0) {
    const div = document.createElement('div');
    div.className = 'tree-node';

    const item = document.createElement('div');
    item.className = 'tree-item';
    item.onclick = (e) => {
        e.stopPropagation();
        selectItem(item, node.id);
    };

    if (level > 0) {
        const placeholder = document.createElement('span');
        placeholder.className = 'tree-placeholder';
        item.appendChild(placeholder);
    }

    item.appendChild(document.createTextNode(node.label));
    div.appendChild(item);

    return div;
}

/**
 * Toggle node expansion
 */
function toggleNode(container, toggle) {
    container.classList.toggle('collapsed');
    toggle.classList.toggle('collapsed');
}

/**
 * Select item
 */
function selectItem(element, id) {
    document.querySelectorAll('.tree-item.active').forEach(item => {
        item.classList.remove('active');
    });

    if (element) {
        element.classList.add('active');
    }

    // Load content
    loadModuleContent(id);
}

/**
 * Load module content
 */
function loadModuleContent(id) {
    const contentPanel = document.getElementById('content-panel');

    contentPanel.innerHTML = `
        <div style="padding: 40px; text-align: center;">
            <h2 style="color: var(--text-light); margin-bottom: 15px;">
                <i class="fas fa-cubes"></i>
            </h2>
            <h3 style="color: var(--text-light);">${id}</h3>
            <p style="color: var(--text-muted); margin-top: 10px;">
                Módulo em desenvolvimento
            </p>
        </div>
    `;
}

/**
 * Logout
 */
function logout() {
    if (confirm('Deseja sair do sistema?')) {
        window.location.href = '{{ url_for("logout") }}';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', buildTreeMenu);
