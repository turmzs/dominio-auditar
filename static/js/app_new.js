// ============================================
// APP CONTROLLER - NEW CLEAN LAYOUT
// ============================================

// Current active tab
let activeTab = 'dashboard';

/**
 * Toggle dropdown menus
 */
function toggleMenu(e, menuId) {
    e.preventDefault();
    e.stopPropagation();

    const menu = document.getElementById(menuId);

    // Close all other menus
    document.querySelectorAll('.dropdown-menu').forEach(m => {
        if (m.id !== menuId) {
            m.classList.remove('show');
        }
    });

    // Toggle current menu
    menu.classList.toggle('show');
}

/**
 * Close all menus when clicking outside
 */
document.addEventListener('click', function (e) {
    if (!e.target.closest('.menu-dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

/**
 * Switch between tabs/sections
 */
function switchTab(tabName) {
    activeTab = tabName;

    // Close all menus
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.classList.remove('show');
    });

    // Load content based on tab
    loadContent(tabName);
}

/**
 * Load content for different tabs
 */
function loadContent(tabName) {
    const contentArea = document.getElementById('dashboard-content');

    if (!contentArea) return;


    switch (tabName) {
        case 'dashboard':
            contentArea.innerHTML = `
                <div class="dashboard-container">
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-icon"><i class="fa-solid fa-file-invoice"></i></div>
                            <div class="kpi-content">
                                <div class="kpi-label">Notas Emitidas</div>
                                <div class="kpi-value">2.347</div>
                                <div class="kpi-subtitle">Maio/2026</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon"><i class="fa-solid fa-money-bill-wave"></i></div>
                            <div class="kpi-content">
                                <div class="kpi-label">Faturamento</div>
                                <div class="kpi-value">R$ 1.2M</div>
                                <div class="kpi-subtitle">Mês atual</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon"><i class="fa-solid fa-percentage"></i></div>
                            <div class="kpi-content">
                                <div class="kpi-label">Impostos</div>
                                <div class="kpi-value">R$ 156K</div>
                                <div class="kpi-subtitle">23,5% do total</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon"><i class="fa-solid fa-check-circle"></i></div>
                            <div class="kpi-content">
                                <div class="kpi-label">Status</div>
                                <div class="kpi-value">Sincronizado</div>
                                <div class="kpi-subtitle">Última atualização: 2h atrás</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'empresas':
            contentArea.innerHTML = `
                <div class="section-container">
                    <div class="section-header">
                        <h2>Gerenciamento de Empresas</h2>
                        <button class="btn-primary" onclick="showAlert('Nova Empresa')">+ Adicionar Empresa</button>
                    </div>
                    <div class="companies-list">
                        <div class="company-card">
                            <div class="company-name">LICING COMERCIO LTDA</div>
                            <div class="company-cnpj">CNPJ: 12.345.678/0001-90</div>
                            <div class="company-status active">● Ativa</div>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'movimentos':
            contentArea.innerHTML = `
                <div class="section-container">
                    <div class="section-header">
                        <h2>Movimentos e Notas Fiscais</h2>
                        <button class="btn-primary" onclick="showAlert('Importar Nota')">+ Importar Nota</button>
                    </div>
                    <div class="table-responsive">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Número</th>
                                    <th>Fornecedor</th>
                                    <th>Valor</th>
                                    <th>CFOP</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>01/05/2026</td>
                                    <td>NF 001234</td>
                                    <td>Fornecedor XYZ</td>
                                    <td>R$ 5.234,00</td>
                                    <td>1.102</td>
                                    <td><span class="badge badge-success">Processada</span></td>
                                </tr>
                                <tr>
                                    <td>02/05/2026</td>
                                    <td>NF 001235</td>
                                    <td>Fornecedor ABC</td>
                                    <td>R$ 3.456,00</td>
                                    <td>1.102</td>
                                    <td><span class="badge badge-success">Processada</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            break;
        case 'relatorios':
            contentArea.innerHTML = `
                <div class="section-container">
                    <div class="section-header">
                        <h2>Relatórios Fiscais</h2>
                        <button class="btn-primary" onclick="showAlert('Gerar Relatório')">Gerar Relatório</button>
                    </div>
                    <div class="reports-grid">
                        <div class="report-card">
                            <i class="fa-solid fa-file-pdf"></i>
                            <h3>SPED Fiscal</h3>
                            <p>Arquivo de contribuições federais</p>
                            <button onclick="showAlert('SPED Fiscal')">Gerar</button>
                        </div>
                        <div class="report-card">
                            <i class="fa-solid fa-chart-bar"></i>
                            <h3>Análise de Tributos</h3>
                            <p>Resumo de impostos do período</p>
                            <button onclick="showAlert('Análise de Tributos')">Gerar</button>
                        </div>
                        <div class="report-card">
                            <i class="fa-solid fa-receipt"></i>
                            <h3>ECF</h3>
                            <p>Escrituração Contábil Fiscal</p>
                            <button onclick="showAlert('ECF')">Gerar</button>
                        </div>
                    </div>
                </div>
            `;
            break;

        case 'apuracao':
            // Consulta de apuração: roda o motor (DRE/memória) via endpoints existentes no app.py
            contentArea.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-triangle-exclamation text-warning"></i><p>Apuração/Consulta requer Empresa Ativa e Período (a UI nova ainda não conecta esses dados como a UI antiga).</p></div>`;
            break;

        case 'consulta_apuracao':
            contentArea.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-triangle-exclamation text-warning"></i><p>Apuração/Consulta requer Empresa Ativa e Período (a UI nova ainda não conecta esses dados como a UI antiga).</p></div>`;
            break;
        case 'utilitarios':
            contentArea.innerHTML = `
                    < div class="section-container" >
                    <div class="section-header">
                        <h2>Utilitários e Ferramentas</h2>
                    </div>
                    <div class="tools-grid">
                        <div class="tool-card">
                            <i class="fa-solid fa-calculator"></i>
                            <h3>Calculadora</h3>
                            <p>Cálculos tributários rápidos</p>
                            <button onclick="showAlert('Calculadora')">Abrir</button>
                        </div>
                        <div class="tool-card">
                            <i class="fa-solid fa-database"></i>
                            <h3>Backup</h3>
                            <p>Fazer backup dos dados</p>
                            <button onclick="showAlert('Backup')">Iniciar</button>
                        </div>
                        <div class="tool-card">
                            <i class="fa-solid fa-sync"></i>
                            <h3>Sincronização</h3>
                            <p>Sincronizar com servidores</p>
                            <button onclick="showAlert('Sincronização')">Sincronizar</button>
                        </div>
                        <div class="tool-card">
                            <i class="fa-solid fa-cloud-upload"></i>
                            <h3>Upload Fiscal</h3>
                            <p>Enviar para portal de impostos</p>
                            <button onclick="showAlert('Upload Fiscal')">Enviar</button>
                        </div>
                    </div>
                </div >
                    `;
            break;
        case 'favoritos':
            contentArea.innerHTML = `
                    < div class="section-container" >
                    <div class="section-header">
                        <h2>Favoritos</h2>
                    </div>
                    <p style="color: var(--text-muted); padding: 20px;">Nenhum favorito adicionado. Use o menu para adicionar atalhos rápidos.</p>
                </div >
                    `;
            break;
        case 'ajuda':
            contentArea.innerHTML = `
                    < div class="section-container" >
                    <div class="section-header">
                        <h2>Ajuda e Documentação</h2>
                    </div>
                    <div class="help-content">
                        <div class="help-section">
                            <h3>Versão do Sistema</h3>
                            <p>Domínio Auditar v10.6A-05-01</p>
                        </div>
                        <div class="help-section">
                            <h3>Documentação</h3>
                            <p><a href="#" onclick="showAlert('Manual')">Acessar Manual Completo</a></p>
                        </div>
                        <div class="help-section">
                            <h3>Suporte</h3>
                            <p>Contate: suporte@dominio.com.br</p>
                        </div>
                    </div>
                </div >
                    `;
            break;
        default:
            contentArea.innerHTML = `< div class="section-content" > Conteúdo não encontrado</div > `;
    }
}

/**
 * Show alert for disabled features
 */
function showAlert(feature) {
    alert(`${feature} - Funcionalidade em desenvolvimento`);
}

// Apuração (Lancamentos vs Consulta)
function loadApuracao(empresaId, mes, ano, apenasConsulta) {
    const contentArea = document.getElementById('dashboard-content');
    if (!contentArea) return;

    contentArea.innerHTML = `< div class="alert-info-box" ><i class="fa-solid fa-spinner fa-spin text-info"></i><p>Processando ${apenasConsulta ? 'Consulta' : 'Apuração'}...</p></div > `;

    // DRE
    Promise.all([
        fetch(`/api/apuracao/dre?empresa_id=${empresaId}&mes=${mes}&ano=${ano}`),
        fetch(`/api/apuracao/memoria?empresa_id=${empresaId}&mes=${mes}&ano=${ano}`)
    ])
        .then(async ([dreRes, memoriaRes]) => {
            const dreData = await dreRes.json();
            const memoriaData = await memoriaRes.json();

            let memoriaHtml = ``;
            if (memoriaData.memoria && memoriaData.memoria.length > 0) {
                memoriaHtml = memoriaData.memoria.map(item => {
                    const details = item.detalhamento && Object.keys(item.detalhamento).length > 0 ? Object.entries(item.detalhamento) : [];
                    const detailsHtml = details.length
                        ? `< div class="mem-details" > <ul>` + details.map(([k, v]) => `<li><strong>${k}:</strong> ${v}</li>`).join('') + `</ul></div > `
                        : ``;
                    return `
                    < div class="memoria-card" >
                            <div class="memoria-card-header" onclick="toggleAccordion(this)">
                                <h4>${item.imposto}</h4>
                                <span>R$ ${item.valor_total}</span>
                            </div>
                            <div class="memoria-card-body" style="display:none;">
                                <div class="mem-row"><span>Base de Cálculo:</span><span>R$ ${item.base_calculo}</span></div>
                                <div class="mem-row"><span>Alíquota:</span><span>${item.aliquota}%</span></div>
                                <div class="mem-row"><span>Total:</span><span>R$ ${item.valor_total}</span></div>
                                ${detailsHtml}
                            </div>
                        </div >
                    `;
                }).join('');
            } else {
                memoriaHtml = `< div class="alert-info-box" > <p>Nenhuma memória de cálculo gerada.</p></div > `;
            }

            contentArea.innerHTML = `
                    < div class="calculation-container" >
                    <div class="calc-col" id="dre-wrapper">${dreData.html || '<div class="alert-info-box">Sem dados de DRE.</div>'}</div>
                    <div class="calc-col">
                        <div class="panel">
                            <div class="panel-header flex-header">
                                <h3><i class="fa-solid fa-microchip text-primary-light"></i> Memória de Cálculo</h3>
                            </div>
                            <div class="panel-body scroll-vertical" id="calc-memoria-wrapper" style="max-height: calc(100vh - 280px);">${memoriaHtml}</div>
                        </div>
                        ${apenasConsulta ? `<div class="text-muted" style="margin-top:10px;">Modo: CONSULTA (sem geração de lançamentos)</div>` : ''}
                        <div class="text-muted" style="margin-top:6px;">Modo: ${apenasConsulta ? 'Consultar Apuração' : 'Apurar / Calcular'}</div>
                    </div>
                </div >
                    `;
        })
        .catch(() => {
            contentArea.innerHTML = `< div class="alert-info-box" ><i class="fa-solid fa-triangle-exclamation text-danger"></i><p>Erro ao calcular apuração.</p></div > `;
        });
}

// usado no HTML gerado acima
function toggleAccordion(header) {
    const body = header.nextElementSibling;
    if (!body) return;
    if (body.style.display === 'none' || !body.style.display) {
        body.style.display = 'flex';
    } else {
        body.style.display = 'none';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    loadContent('dashboard');
});

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    if (e.key === 'F8') {
        e.preventDefault();
        alert('Trocar empresa (F8)');
    }
});
