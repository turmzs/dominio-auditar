/* ============================================
   CORPORATE FISCAL SYSTEM - JAVASCRIPT
   ============================================ */

// Current active module
let activeModule = 'dashboard';
let selectedRows = new Set();
let currentData = [];

/**
 * Switch module/view
 */
function switchModule(e, moduleName) {
    e.preventDefault();

    activeModule = moduleName;

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-module="${moduleName}"]`).classList.add('active');

    // Load module content
    loadModule(moduleName);
}

/**
 * Load module content dynamically
 */
function loadModule(moduleName) {
    const container = document.getElementById('module-container');

    switch (moduleName) {
        case 'dashboard':
            container.innerHTML = renderDashboard();
            break;
        case 'escrita':
        case 'entradas':
        case 'saidas':
            container.innerHTML = renderFiscalGrid(moduleName);
            initGridEvents();
            break;
        case 'servicos':
            container.innerHTML = renderServicesGrid();
            initGridEvents();
            break;
        case 'apuracao':
            container.innerHTML = renderApuracaoGrid();
            initGridEvents();
            break;
        case 'sped':
            container.innerHTML = renderSPEDModule();
            break;
        case 'cadastros':
            container.innerHTML = renderCadastrosModule();
            break;
        case 'relatorios':
            container.innerHTML = renderRelatoriosModule();
            break;
        case 'config':
            container.innerHTML = renderConfigModule();
            break;
        default:
            container.innerHTML = '<div style="padding: 20px;">Módulo não encontrado</div>';
    }
}

/**
 * Render Dashboard
 */
function renderDashboard() {
    return `
        <div style="padding: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
            <div style="border: 1px solid #c0c0c0; padding: 12px; background: white;">
                <div style="font-weight: 600; color: #0066cc; margin-bottom: 8px;">
                    <i class="fas fa-file-invoice"></i> Notas Emitidas
                </div>
                <div style="font-size: 24px; font-weight: 700;">2.347</div>
                <div style="font-size: 11px; color: #666;">Maio/2026</div>
            </div>
            <div style="border: 1px solid #c0c0c0; padding: 12px; background: white;">
                <div style="font-weight: 600; color: #0066cc; margin-bottom: 8px;">
                    <i class="fas fa-money-bill"></i> Faturamento
                </div>
                <div style="font-size: 24px; font-weight: 700;">R$ 1,2M</div>
                <div style="font-size: 11px; color: #666;">Mês atual</div>
            </div>
            <div style="border: 1px solid #c0c0c0; padding: 12px; background: white;">
                <div style="font-weight: 600; color: #0066cc; margin-bottom: 8px;">
                    <i class="fas fa-percent"></i> Impostos
                </div>
                <div style="font-size: 24px; font-weight: 700;">R$ 156K</div>
                <div style="font-size: 11px; color: #666;">23,5% do total</div>
            </div>
        </div>
    `;
}

/**
 * Render Fiscal Grid (Escrita, Entradas, Saídas)
 */
function renderFiscalGrid(type) {
    return `
        <div class="filter-bar">
            <div class="filter-group">
                <label class="filter-label">Período:</label>
                <input type="date" class="filter-input" value="2026-05-01">
                <span style="font-size: 11px;">até</span>
                <input type="date" class="filter-input" value="2026-05-31">
            </div>
            <div class="filter-group">
                <label class="filter-label">Situação:</label>
                <select class="filter-select">
                    <option>Todos</option>
                    <option>Processada</option>
                    <option>Pendente</option>
                    <option>Erro</option>
                </select>
            </div>
        </div>
        
        <div class="toolbar">
            <button class="btn-toolbar"><i class="fas fa-plus"></i> Incluir</button>
            <button class="btn-toolbar"><i class="fas fa-edit"></i> Alterar</button>
            <button class="btn-toolbar"><i class="fas fa-trash"></i> Excluir</button>
            <div style="width: 1px; background: #c0c0c0;"></div>
            <button class="btn-toolbar"><i class="fas fa-upload"></i> Importar XML</button>
            <button class="btn-toolbar"><i class="fas fa-cog"></i> Processar</button>
            <button class="btn-toolbar"><i class="fas fa-sync"></i> Atualizar</button>
            <button class="btn-toolbar"><i class="fas fa-download"></i> Exportar Excel</button>
        </div>
        
        <div class="grid-area">
            <div class="grid-wrapper">
                <table class="data-grid">
                    <thead>
                        <tr>
                            <th><input type="checkbox" onchange="toggleSelectAll(this)"></th>
                            <th onclick="sortGrid(this)">Data</th>
                            <th onclick="sortGrid(this)">Documento</th>
                            <th onclick="sortGrid(this)">Série</th>
                            <th onclick="sortGrid(this)">Fornecedor/Cliente</th>
                            <th onclick="sortGrid(this)">CNPJ</th>
                            <th onclick="sortGrid(this)">CFOP</th>
                            <th onclick="sortGrid(this)">NCM</th>
                            <th onclick="sortGrid(this)">Valor Contábil</th>
                            <th onclick="sortGrid(this)">Base ICMS</th>
                            <th onclick="sortGrid(this)">Valor ICMS</th>
                            <th onclick="sortGrid(this)">Base ST</th>
                            <th onclick="sortGrid(this)">Valor ST</th>
                            <th onclick="sortGrid(this)">Situação</th>
                        </tr>
                    </thead>
                    <tbody id="grid-body">
                        <tr>
                            <td><input type="checkbox" class="row-checkbox" onchange="toggleRow(this)"></td>
                            <td>01/05/2026</td>
                            <td>NF 001234</td>
                            <td>1</td>
                            <td>Fornecedor XYZ LTDA</td>
                            <td>12.345.678/0001-90</td>
                            <td>1.102</td>
                            <td>27.10.19</td>
                            <td>5.234,00</td>
                            <td>5.234,00</td>
                            <td>627,00</td>
                            <td>-</td>
                            <td>-</td>
                            <td><span style="color: green;">✓ Processada</span></td>
                        </tr>
                        <tr>
                            <td><input type="checkbox" class="row-checkbox" onchange="toggleRow(this)"></td>
                            <td>02/05/2026</td>
                            <td>NF 001235</td>
                            <td>1</td>
                            <td>Fornecedor ABC LTDA</td>
                            <td>98.765.432/0001-10</td>
                            <td>1.102</td>
                            <td>82.02.10</td>
                            <td>3.456,00</td>
                            <td>3.456,00</td>
                            <td>414,72</td>
                            <td>-</td>
                            <td>-</td>
                            <td><span style="color: green;">✓ Processada</span></td>
                        </tr>
                        <tr>
                            <td><input type="checkbox" class="row-checkbox" onchange="toggleRow(this)"></td>
                            <td>03/05/2026</td>
                            <td>NF 001236</td>
                            <td>1</td>
                            <td>Fornecedor DEF LTDA</td>
                            <td>55.555.555/0001-55</td>
                            <td>1.102</td>
                            <td>39.01.10</td>
                            <td>8.900,00</td>
                            <td>8.900,00</td>
                            <td>1.068,00</td>
                            <td>-</td>
                            <td>-</td>
                            <td><span style="color: orange;">⚠ Pendente</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="bottom-panel">
                <div class="tab-bar">
                    <button class="tab active" onclick="switchTab(event, 'produtos')">Produtos</button>
                    <button class="tab" onclick="switchTab(event, 'impostos')">Impostos</button>
                    <button class="tab" onclick="switchTab(event, 'observacoes')">Observações</button>
                    <button class="tab" onclick="switchTab(event, 'historico')">Histórico</button>
                    <button class="tab" onclick="switchTab(event, 'xml')">XML</button>
                    <button class="tab" onclick="switchTab(event, 'eventos')">Eventos</button>
                </div>
                
                <div class="tab-content" id="produtos">
                    <div class="detail-grid">
                        <div class="detail-field">
                            <div class="detail-label">Produto</div>
                            <div class="detail-value">Produto A</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-label">Quantidade</div>
                            <div class="detail-value">100,00</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-label">Valor Unit.</div>
                            <div class="detail-value">R$ 52,34</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-label">Valor Total</div>
                            <div class="detail-value">R$ 5.234,00</div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content hidden" id="impostos">
                    <div class="detail-grid">
                        <div class="detail-field">
                            <div class="detail-label">ICMS</div>
                            <div class="detail-value">R$ 627,00</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-label">Alíquota</div>
                            <div class="detail-value">12%</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-label">IPI</div>
                            <div class="detail-value">R$ 0,00</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-label">PIS</div>
                            <div class="detail-value">R$ 0,00</div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content hidden" id="observacoes">
                    <p style="color: #666; font-size: 11px;">Nenhuma observação</p>
                </div>
                
                <div class="tab-content hidden" id="historico">
                    <p style="color: #666; font-size: 11px;">Arquivo criado em 01/05/2026 às 14:30:45</p>
                </div>
                
                <div class="tab-content hidden" id="xml">
                    <pre style="font-size: 9px; background: #f0f0f0; padding: 8px; overflow: auto; max-height: 150px;">
&lt;NFe&gt;
  &lt;infNFe Id="NFe12345678901234567890123456789012345678901234"&gt;
    &lt;ide&gt;
      &lt;dEmi&gt;2026-05-01&lt;/dEmi&gt;
      &lt;dSaiEnt&gt;2026-05-01&lt;/dSaiEnt&gt;
    &lt;/ide&gt;
  &lt;/infNFe&gt;
&lt;/NFe&gt;
                    </pre>
                </div>
                
                <div class="tab-content hidden" id="eventos">
                    <p style="color: #666; font-size: 11px;">Sem eventos registrados</p>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render Services Grid
 */
function renderServicesGrid() {
    return `<div style="padding: 20px;">Módulo de Serviços em desenvolvimento...</div>`;
}

/**
 * Render Apuração Grid
 */
function renderApuracaoGrid() {
    return `<div style="padding: 20px;">Módulo de Apuração em desenvolvimento...</div>`;
}

/**
 * Render SPED Module
 */
function renderSPEDModule() {
    return `<div style="padding: 20px;">Módulo SPED Fiscal em desenvolvimento...</div>`;
}

/**
 * Render Cadastros Module
 */
function renderCadastrosModule() {
    return `<div style="padding: 20px;">Módulo de Cadastros em desenvolvimento...</div>`;
}

/**
 * Render Relatórios Module
 */
function renderRelatoriosModule() {
    return `<div style="padding: 20px;">Módulo de Relatórios em desenvolvimento...</div>`;
}

/**
 * Render Configurações Module
 */
function renderConfigModule() {
    return `<div style="padding: 20px;">Módulo de Configurações em desenvolvimento...</div>`;
}

/**
 * Initialize grid events
 */
function initGridEvents() {
    // Implementar eventos de grid
}

/**
 * Toggle row selection
 */
function toggleRow(checkbox) {
    checkbox.parentElement.parentElement.classList.toggle('selected');
}

/**
 * Toggle select all
 */
function toggleSelectAll(checkbox) {
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = checkbox.checked;
        cb.onchange();
    });
}

/**
 * Switch tab
 */
function switchTab(e, tabName) {
    e.preventDefault();

    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.remove('hidden');
    e.target.classList.add('active');
}

/**
 * Sort grid
 */
function sortGrid(header) {
    console.log('Sorting by:', header.textContent);
}

/**
 * Logout
 */
function logout() {
    if (confirm('Deseja sair do sistema?')) {
        window.location.href = '{{ url_for("logout") }}';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    loadModule('dashboard');
});
