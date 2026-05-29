// State variables
let currentCompanyId = null;
let currentMonth = new Date().getMonth() + 1; // 1-indexed
let currentYear = 2026;
let regimesChart = null;

// On document load
document.addEventListener("DOMContentLoaded", () => {
    initApp();
    setupXMLDropzone();
});

function initApp() {
    // Set default values in Period dropdowns
    document.getElementById("select-mes").value = currentMonth;
    document.getElementById("select-ano").value = currentYear;
    
    // Load companies
    loadEmpresas();
}

// Tab Switching
function switchTab(tabId) {
    // Toggle active tab buttons
    document.querySelectorAll(".nav-item").forEach(btn => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`btn-tab-${tabId}`);
    if (activeBtn) activeBtn.classList.add("active");

    // Toggle active tab content panels
    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active-tab"));
    document.getElementById(`tab-${tabId}`).classList.add("active-tab");

    // Load data based on selected tab
    if (tabId === "dashboard") {
        loadDashboardData();
    } else if (tabId === "notas") {
        loadInvoices();
    } else if (tabId === "apuracao") {
        loadApuracaoDetails();
    } else if (tabId === "empresas") {
        loadEmpresasTab();
    }
    
    // Update simulated desktop status
    updateDesktopStatus(tabId);
}

// Period / Company Dropdown actions
function onEmpresaChanged() {
    const selector = document.getElementById("select-empresa");
    currentCompanyId = selector.value ? parseInt(selector.value) : null;
    
    // Save to localStorage
    if (currentCompanyId) {
        localStorage.setItem("active_company_id", currentCompanyId);
    }
    
    updateDesktopStatus();
    refreshCurrentTab();
}

function onPeriodChanged() {
    currentMonth = parseInt(document.getElementById("select-mes").value);
    currentYear = parseInt(document.getElementById("select-ano").value);
    
    updateDesktopStatus();
    refreshCurrentTab();
}

function refreshCurrentTab() {
    // Identify which tab is currently active
    const activeTab = document.querySelector(".nav-item.active");
    if (!activeTab) return;
    
    const tabId = activeTab.id.replace("btn-tab-", "");
    switchTab(tabId);
}

// Sincroniza informações no cabeçalho da janela desktop simulada
function updateDesktopStatus(tabId) {
    const selectEmp = document.getElementById("select-empresa");
    const companyPill = document.getElementById("active-company-name-pill");
    if (selectEmp && companyPill) {
        if (selectEmp.selectedIndex >= 0 && selectEmp.value) {
            companyPill.textContent = selectEmp.options[selectEmp.selectedIndex].text;
        } else {
            companyPill.textContent = "Sem Empresa Ativa";
        }
    }
    
    const selectMes = document.getElementById("select-mes");
    const selectAno = document.getElementById("select-ano");
    const periodPill = document.getElementById("active-period-pill");
    if (selectMes && selectAno && periodPill) {
        const mesStr = selectMes.options[selectMes.selectedIndex].text;
        const anoStr = selectAno.value;
        periodPill.textContent = `Competência: ${mesStr}/${anoStr}`;
    }
    
    const windowTitle = document.getElementById("active-window-title");
    if (windowTitle) {
        let title = "Painel Geral - Resumo Fiscal";
        const currentTab = tabId || (document.querySelector(".nav-item.active") ? document.querySelector(".nav-item.active").id.replace("btn-tab-", "") : "dashboard");
        
        if (currentTab === "dashboard") title = "Painel Geral - Resumo Fiscal";
        else if (currentTab === "notas") title = "Movimentos - Escrituração (XML)";
        else if (currentTab === "apuracao") title = "Relatórios - Apuração & DRE";
        else if (currentTab === "empresas") title = "Arquivos - Cadastro de Empresas";
        
        windowTitle.innerHTML = `<i class="fa-solid fa-folder-open text-gold"></i> ${title}`;
    }

    // Marca botão ativo na barra de ferramentas
    document.querySelectorAll(".toolbar-btn").forEach(btn => btn.classList.remove("active-btn"));
    const activeTabId = tabId || (document.querySelector(".nav-item.active") ? document.querySelector(".nav-item.active").id.replace("btn-tab-", "") : "dashboard");
    
    // Tratamento para Entradas/Saídas que são subset da aba 'notas'
    let toolbarTargetId = `toolbar-btn-${activeTabId}`;
    const activeToolbarBtn = document.getElementById(toolbarTargetId);
    if (activeToolbarBtn) activeToolbarBtn.classList.add("active-btn");
}

// ==========================================
// COMPANIES MANAGEMENT
// ==========================================

function loadEmpresas() {
    fetch("/api/empresas")
        .then(res => res.json())
        .then(data => {
            const dropdown = document.getElementById("select-empresa");
            dropdown.innerHTML = "";
            
            if (data.length === 0) {
                dropdown.innerHTML = `<option value="">Nenhuma Empresa Cadastrada</option>`;
                currentCompanyId = null;
                switchTab("empresas");
                return;
            }
            
            data.forEach(emp => {
                const opt = document.createElement("option");
                opt.value = emp.id;
                opt.textContent = `${emp.nome} (${emp.cnpj})`;
                dropdown.appendChild(opt);
            });

            // Retrieve last active company from localStorage if valid
            const cachedId = localStorage.getItem("active_company_id");
            if (cachedId && data.some(emp => emp.id == cachedId)) {
                dropdown.value = cachedId;
            }
            
            currentCompanyId = parseInt(dropdown.value);
            refreshCurrentTab();
        })
        .catch(err => console.error("Erro ao carregar empresas:", err));
}

function loadEmpresasTab() {
    fetch("/api/empresas")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("empresas-cards-container");
            container.innerHTML = "";
            
            if (data.length === 0) {
                container.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-building"></i><p>Nenhuma empresa cadastrada. Use o formulário acima para registrar sua primeira empresa.</p></div>`;
                return;
            }
            
            data.forEach(emp => {
                const isActive = emp.id === currentCompanyId;
                const card = document.createElement("div");
                card.className = `empresa-card glass ${isActive ? 'active-card' : ''}`;
                
                let regimeLabel = "";
                if (emp.regime === "simples") regimeLabel = "Simples Nacional";
                else if (emp.regime === "presumido") regimeLabel = "Lucro Presumido";
                else if (emp.regime === "real") regimeLabel = "Lucro Real";
                
                let atividadeLabel = "";
                if (emp.atividade === "servicos") atividadeLabel = "Serviços";
                else if (emp.atividade === "comercio") atividadeLabel = "Comércio";
                else if (emp.atividade === "fator_r") atividadeLabel = "Serviços Intelectuais (Fator R)";

                card.innerHTML = `
                    <div class="empresa-card-info">
                        <h4>${emp.nome}</h4>
                        <p><strong>CNPJ:</strong> ${emp.cnpj} | <strong>Regime:</strong> ${regimeLabel}</p>
                        <p><strong>Atividade:</strong> ${atividadeLabel} | <strong>RBT12:</strong> R$ ${formatMoeda(emp.faturamento_anual)}</p>
                    </div>
                    <div class="empresa-card-actions">
                        <button class="btn-action" title="Editar Empresa" onclick="editEmpresa(${JSON.stringify(emp).replace(/"/g, '&quot;')})">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn-action trash" title="Excluir Empresa" onclick="deleteEmpresa(${emp.id})">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                `;
                container.appendChild(card);
            });
        });
}

function toggleFormRegimeDetails() {
    const regime = document.getElementById("empresa-regime").value;
    const payrollGroup = document.getElementById("payroll-group");
    const activity = document.getElementById("empresa-atividade").value;
    
    if (regime === "simples" && activity === "fator_r") {
        payrollGroup.style.display = "flex";
    } else {
        payrollGroup.style.display = "none";
    }
}

// Listener for activity field changes to update payroll field visibility
document.getElementById("empresa-atividade").addEventListener("change", toggleFormRegimeDetails);

function saveEmpresa(event) {
    event.preventDefault();
    
    const id = document.getElementById("empresa-id").value;
    const nome = document.getElementById("empresa-nome").value;
    const cnpj = document.getElementById("empresa-cnpj").value;
    const regime = document.getElementById("empresa-regime").value;
    const atividade = document.getElementById("empresa-atividade").value;
    const faturamento_anual = parseFloat(document.getElementById("empresa-faturamento-anual").value) || 0;
    const folha_anual = parseFloat(document.getElementById("empresa-folha-anual").value) || 0;

    const payload = { id, nome, cnpj, regime, atividade, faturamento_anual, folha_anual };

    fetch("/api/empresas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        clearEmpresaForm();
        loadEmpresas();
        loadEmpresasTab();
    })
    .catch(err => console.error("Erro ao salvar empresa:", err));
}

function editEmpresa(emp) {
    document.getElementById("empresa-id").value = emp.id;
    document.getElementById("empresa-nome").value = emp.nome;
    document.getElementById("empresa-cnpj").value = emp.cnpj;
    document.getElementById("empresa-regime").value = emp.regime;
    document.getElementById("empresa-atividade").value = emp.atividade;
    document.getElementById("empresa-faturamento-anual").value = emp.faturamento_anual;
    document.getElementById("empresa-folha-anual").value = emp.folha_anual;
    
    document.getElementById("empresa-form-title").innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Editar Empresa`;
    toggleFormRegimeDetails();
}

function deleteEmpresa(id) {
    if (!confirm("Tem certeza que deseja excluir esta empresa e todos os seus lançamentos fiscais?")) return;
    
    fetch(`/api/empresas/${id}`, { method: "DELETE" })
        .then(() => {
            loadEmpresas();
            loadEmpresasTab();
        });
}

function clearEmpresaForm() {
    document.getElementById("empresa-id").value = "";
    document.getElementById("form-empresa").reset();
    document.getElementById("empresa-form-title").innerHTML = `<i class="fa-solid fa-folder-plus"></i> Cadastrar Nova Empresa`;
    toggleFormRegimeDetails();
}

// ==========================================
// DASHBOARD DETAILS & COMPUTATIONS
// ==========================================

function loadDashboardData() {
    if (!currentCompanyId) return;

    // Load main KPIs
    fetch(`/api/dashboard?empresa_id=${currentCompanyId}&mes=${currentMonth}&ano=${currentYear}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("kpi-receita-mensal").textContent = `R$ ${formatMoeda(data.receita_bruta)}`;
            document.getElementById("kpi-total-impostos").textContent = `R$ ${formatMoeda(data.total_impostos)}`;
            document.getElementById("kpi-lucro-liquido").textContent = `R$ ${formatMoeda(data.lucro_liquido)}`;
            document.getElementById("kpi-carga-efetiva").textContent = `${data.carga_efetiva.toFixed(2)}%`;
            document.getElementById("kpi-regime-label").textContent = `Regime: ${data.regime}`;

            // Handle Simples Progress Box
            const progressBox = document.getElementById("simples-progress-box");
            if (data.regime_tipo === "simples") {
                progressBox.classList.remove("display-none");
                document.getElementById("simples-progress-faturamento-anual").textContent = `Faturamento Acumulado (12m): R$ ${formatMoeda(data.faturamento_anual)}`;
                
                // R$ 3.6M sublimite
                const subPercent = Math.min(100, (data.faturamento_anual / 3600000) * 100);
                document.getElementById("sublimite-progress").style.width = `${subPercent}%`;
                document.getElementById("sublimite-percent-label").textContent = `${subPercent.toFixed(1)}% (R$ 3.6M)`;

                // R$ 4.8M limit
                const limPercent = Math.min(100, (data.faturamento_anual / 4800000) * 100);
                document.getElementById("limite-progress").style.width = `${limPercent}%`;
                document.getElementById("limite-percent-label").textContent = `${limPercent.toFixed(1)}% (R$ 4.8M)`;
            } else {
                progressBox.classList.add("display-none");
            }

            // Alerts Panel
            const alertsContainer = document.getElementById("alerts-container");
            alertsContainer.innerHTML = "";
            
            if (data.alertas.length === 0) {
                alertsContainer.innerHTML = `
                    <div class="alert-info-box">
                        <i class="fa-solid fa-circle-check text-success"></i>
                        <div>
                            <h5>Sem irregularidades detectadas</h5>
                            <p>As notas fiscais declaradas estão em conformidade com as regras fiscais do regime de ${data.regime}.</p>
                        </div>
                    </div>
                `;
            } else {
                data.alertas.forEach(alert => {
                    const alertDiv = document.createElement("div");
                    alertDiv.className = `alert-box ${alert.tipo}`; // info, warning, danger
                    
                    let iconClass = "fa-solid fa-circle-info text-info";
                    if (alert.tipo === "warning") iconClass = "fa-solid fa-triangle-exclamation text-warning";
                    if (alert.tipo === "danger") iconClass = "fa-solid fa-circle-xmark text-danger";
                    
                    alertDiv.innerHTML = `
                        <i class="${iconClass}"></i>
                        <div>
                            <h5>${alert.titulo}</h5>
                            <p>${alert.descricao}</p>
                        </div>
                    `;
                    alertsContainer.appendChild(alertDiv);
                });
            }
        });

    // Render/Update Comparison Chart
    fetch(`/api/comparativo?empresa_id=${currentCompanyId}&mes=${currentMonth}&ano=${currentYear}`)
        .then(res => res.json())
        .then(data => {
            renderRegimesChart(data);
        });
}

function renderRegimesChart(chartData) {
    const ctx = document.getElementById("chart-regimes").getContext("2d");
    
    // Destroy previous instance
    if (regimesChart) {
        regimesChart.destroy();
    }

    // Chart.js configuration
    regimesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Simples Nacional', 'Lucro Presumido', 'Lucro Real'],
            datasets: [{
                label: 'Impostos Totais (R$)',
                data: [chartData.simples, chartData.presumido, chartData.real],
                backgroundColor: [
                    'rgba(56, 189, 248, 0.45)',  // Cyan glass
                    'rgba(192, 132, 252, 0.45)', // Purple glass
                    'rgba(52, 211, 153, 0.45)'   // Green glass
                ],
                borderColor: [
                    '#38bdf8',
                    '#c084fc',
                    '#34d399'
                ],
                borderWidth: 1.5,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.85)',
                    titleFont: { family: 'Outfit', size: 13, weight: 'bold' },
                    bodyFont: { family: 'Plus Jakarta Sans', size: 12 },
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return ` R$ ${formatMoeda(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit', weight: '600' } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { 
                        color: '#94a3b8', 
                        font: { family: 'Plus Jakarta Sans' },
                        callback: function(value) {
                            return 'R$ ' + formatMoeda(value);
                        }
                    }
                }
            }
        }
    });
}

// ==========================================
// INVOICES LEDGER & XML PARSING
// ==========================================

function loadInvoices() {
    if (!currentCompanyId) return;

    fetch(`/api/notas?empresa_id=${currentCompanyId}&mes=${currentMonth}&ano=${currentYear}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("invoices-tbody");
            tbody.innerHTML = "";

            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-muted" style="text-align: center; padding: 32px;"><i class="fa-solid fa-box-open" style="font-size: 1.8rem; margin-bottom: 8px; display: block;"></i>Nenhuma nota escriturada neste período. Arraste XMLs acima para começar.</td></tr>`;
                return;
            }

            data.forEach(n => {
                const tr = document.createElement("tr");
                const badgeClass = n.tipo === "saida" ? "badge-out" : "badge-in";
                const badgeLabel = n.tipo === "saida" ? "Saída (Venda)" : "Entrada (Compra)";

                // Convert Date YYYY-MM-DD to DD/MM/YYYY
                const dateParts = n.data_emissao.split("-");
                const formattedDate = dateParts.length === 3 ? `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}` : n.data_emissao;

                tr.innerHTML = `
                    <td>${formattedDate}</td>
                    <td><strong>#${n.numero}</strong></td>
                    <td><span class="badge ${badgeClass}">${badgeLabel}</span></td>
                    <td><code style="background: rgba(255,255,255,0.03); padding: 2px 6px; border-radius: 4px;">${n.cfop || '-'}</code></td>
                    <td title="${n.emitente_cnpj}">${n.emitente_nome || '-'}</td>
                    <td title="${n.destinatario_cnpj}">${n.destinatario_nome || '-'}</td>
                    <td class="text-right"><strong>R$ ${formatMoeda(n.valor_total)}</strong></td>
                    <td class="text-right">
                        <button class="btn-action trash" title="Excluir Nota" onclick="deleteInvoice(${n.id})">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function filterInvoicesTable() {
    const query = document.getElementById("search-invoices").value.toLowerCase();
    const typeFilter = document.getElementById("filter-tipo").value;
    const rows = document.querySelectorAll("#invoices-tbody tr");

    rows.forEach(row => {
        // Skip empty table messages
        if (row.cells.length < 5) return;

        const date = row.cells[0].textContent.toLowerCase();
        const number = row.cells[1].textContent.toLowerCase();
        const type = row.cells[2].textContent.toLowerCase();
        const cfop = row.cells[3].textContent.toLowerCase();
        const issuer = row.cells[4].textContent.toLowerCase();
        const recipient = row.cells[5].textContent.toLowerCase();
        const value = row.cells[6].textContent.toLowerCase();

        const matchesQuery = (
            date.includes(query) || number.includes(query) ||
            cfop.includes(query) || issuer.includes(query) ||
            recipient.includes(query) || value.includes(query)
        );

        let matchesType = true;
        if (typeFilter === "saida") {
            matchesType = type.includes("saída") || type.includes("venda");
        } else if (typeFilter === "entrada") {
            matchesType = type.includes("entrada") || type.includes("compra");
        }

        if (matchesQuery && matchesType) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

function deleteInvoice(id) {
    if (!confirm("Confirmar a exclusão desta nota fiscal da escrituração?")) return;

    fetch(`/api/notas/${id}`, { method: "DELETE" })
        .then(() => loadInvoices());
}

// ==========================================
// DRAG & DROP XML UPLOADER
// ==========================================

function setupXMLDropzone() {
    const dropzone = document.getElementById("xml-dropzone");
    const fileInput = document.getElementById("file-input");

    dropzone.addEventListener("click", () => fileInput.click());
    
    fileInput.addEventListener("change", (e) => {
        handleXMLFiles(e.target.files);
    });

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        handleXMLFiles(e.dataTransfer.files);
    });
}

function handleXMLFiles(files) {
    if (!currentCompanyId) {
        alert("Cadastre e selecione uma Empresa Ativa antes de importar XMLs.");
        return;
    }

    const xmlFiles = Array.from(files).filter(file => file.name.endsWith(".xml"));
    if (xmlFiles.length === 0) return;

    const progressContainer = document.getElementById("upload-progress-container");
    progressContainer.innerHTML = "";
    progressContainer.style.display = "flex";

    let uploadsCompleted = 0;

    xmlFiles.forEach((file, index) => {
        const itemDiv = document.createElement("div");
        itemDiv.className = "upload-progress-item";
        itemDiv.innerHTML = `
            <div class="progress-header-info">
                <span><i class="fa-solid fa-file-code text-info"></i> ${file.name}</span>
                <span id="prog-val-${index}">Carregando...</span>
            </div>
            <div class="progress-bar-track">
                <div id="prog-fill-${index}" class="progress-fill" style="width: 10%"></div>
            </div>
        `;
        progressContainer.appendChild(itemDiv);

        // Read file contents as Text to POST
        const reader = new FileReader();
        reader.onload = (e) => {
            const xmlContent = e.target.result;
            
            document.getElementById(`prog-fill-${index}`).style.width = "40%";
            document.getElementById(`prog-val-${index}`).textContent = "Processando XML...";

            // Post content to API
            fetch("/api/upload", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    empresa_id: currentCompanyId,
                    filename: file.name,
                    xml_content: xmlContent
                })
            })
            .then(res => res.json())
            .then(result => {
                const fill = document.getElementById(`prog-fill-${index}`);
                const status = document.getElementById(`prog-val-${index}`);
                
                if (result.success) {
                    fill.style.width = "100%";
                    fill.style.background = "var(--accent-green)";
                    status.innerHTML = `<span class="text-success"><i class="fa-solid fa-circle-check"></i> Importado (Nota #${result.nota_numero})</span>`;
                } else {
                    fill.style.width = "100%";
                    fill.style.background = "var(--accent-red)";
                    status.innerHTML = `<span class="text-danger" title="${result.message}"><i class="fa-solid fa-circle-xmark"></i> Erro: Duplicada/Inválida</span>`;
                }
            })
            .catch(err => {
                const fill = document.getElementById(`prog-fill-${index}`);
                const status = document.getElementById(`prog-val-${index}`);
                fill.style.width = "100%";
                fill.style.background = "var(--accent-red)";
                status.innerHTML = `<span class="text-danger"><i class="fa-solid fa-circle-xmark"></i> Falha na Conexão</span>`;
            })
            .finally(() => {
                uploadsCompleted++;
                if (uploadsCompleted === xmlFiles.length) {
                    setTimeout(() => {
                        progressContainer.style.display = "none";
                        loadInvoices();
                    }, 4000);
                }
            });
        };
        reader.readAsText(file);
    });
}

// Manual Invoice Modal Actions
function openManualInvoiceModal() {
    document.getElementById("form-invoice").reset();
    
    // Set default date to active period
    const defaultDate = `${currentYear}-${String(currentMonth).padStart(2, '0')}-01`;
    document.getElementById("invoice-data").value = defaultDate;
    
    document.getElementById("modal-invoice").classList.add("active");
}

function closeManualInvoiceModal() {
    document.getElementById("modal-invoice").classList.remove("active");
}

function saveManualInvoice(event) {
    event.preventDefault();

    if (!currentCompanyId) return;

    const payload = {
        empresa_id: currentCompanyId,
        numero: document.getElementById("invoice-numero").value,
        data_emissao: document.getElementById("invoice-data").value,
        tipo: document.getElementById("invoice-tipo").value,
        emitente_nome: document.getElementById("invoice-emitente-nome").value,
        emitente_cnpj: document.getElementById("invoice-emitente-cnpj").value,
        destinatario_nome: document.getElementById("invoice-destinatario-nome").value,
        destinatario_cnpj: document.getElementById("invoice-destinatario-cnpj").value,
        cfop: document.getElementById("invoice-cfop").value,
        valor_total: parseFloat(document.getElementById("invoice-valor").value) || 0,
        valor_iss: parseFloat(document.getElementById("invoice-iss").value) || 0,
        valor_icms: parseFloat(document.getElementById("invoice-icms").value) || 0,
        valor_pis: parseFloat(document.getElementById("invoice-pis").value) || 0,
        valor_cofins: parseFloat(document.getElementById("invoice-cofins").value) || 0,
        valor_csll: parseFloat(document.getElementById("invoice-csll").value) || 0,
        xml_origem: "manual"
    };

    fetch("/api/notas/manual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        closeManualInvoiceModal();
        loadInvoices();
    })
    .catch(err => console.error("Erro ao salvar nota manual:", err));
}

// ==========================================
// APURAÇÃO & DRE COMPILATION
// ==========================================

function loadApuracaoDetails() {
    if (!currentCompanyId) return;

    const dreWrapper = document.getElementById("dre-wrapper");
    const memWrapper = document.getElementById("calc-memoria-wrapper");
    
    dreWrapper.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-spinner fa-spin text-info"></i><p>Calculando apuração tributária...</p></div>`;
    memWrapper.innerHTML = "";

    // 1. Load DRE
    fetch(`/api/apuracao/dre?empresa_id=${currentCompanyId}&mes=${currentMonth}&ano=${currentYear}`)
        .then(res => res.json())
        .then(data => {
            if (data.html) {
                dreWrapper.innerHTML = data.html;
            } else {
                dreWrapper.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-triangle-exclamation text-warning"></i><p>Nenhum dado tributário computado.</p></div>`;
            }
        })
        .catch(err => {
            dreWrapper.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-triangle-exclamation text-danger"></i><p>Erro de conexão com o cálculo.</p></div>`;
        });

    // 2. Load Memória
    fetch(`/api/apuracao/memoria?empresa_id=${currentCompanyId}&mes=${currentMonth}&ano=${currentYear}`)
        .then(res => res.json())
        .then(data => {
            memWrapper.innerHTML = "";
            if (data.memoria && data.memoria.length > 0) {
                data.memoria.forEach(item => {
                    const card = document.createElement("div");
                    card.className = "memoria-card";
                    
                    let detailsListHtml = "";
                    if (item.detalhamento && Object.keys(item.detalhamento).length > 0) {
                        detailsListHtml = `<div class="mem-details"><ul>`;
                        for (const [key, value] of Object.entries(item.detalhamento)) {
                            const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                            
                            let formattedValue = value;
                            if (typeof value === "number" && !key.toLowerCase().includes("faixa") && !key.toLowerCase().includes("aliquota") && !key.toLowerCase().includes("fator")) {
                                formattedValue = `R$ ${formatMoeda(value)}`;
                            } else if (typeof value === "number") {
                                formattedValue = value.toFixed(2);
                            }
                            
                            detailsListHtml += `<li><strong>${formattedKey}:</strong> ${formattedValue}</li>`;
                        }
                        detailsListHtml += `</ul></div>`;
                    }

                    card.innerHTML = `
                        <div class="memoria-card-header" onclick="toggleAccordion(this)">
                            <h4>${item.imposto}</h4>
                            <span>R$ ${formatMoeda(item.valor_total)} <i class="fa-solid fa-chevron-down text-muted" style="font-size: 0.8rem; margin-left: 8px;"></i></span>
                        </div>
                        <div class="memoria-card-body" style="display: none;">
                            <div class="mem-row">
                                <span>Base de Cálculo:</span>
                                <span>R$ ${formatMoeda(item.base_calculo)}</span>
                            </div>
                            <div class="mem-row">
                                <span>Alíquota de Aplicação:</span>
                                <span>${item.aliquota.toFixed(2)}%</span>
                            </div>
                            <div class="mem-row">
                                <span>Débito Inicial:</span>
                                <span>R$ ${formatMoeda(item.valor_debito)}</span>
                            </div>
                            <div class="mem-row">
                                <span>Créditos / Compensações:</span>
                                <span>R$ ${formatMoeda(item.valor_credito)}</span>
                            </div>
                            <div class="mem-row mem-row total">
                                <span>Total Tributado:</span>
                                <span>R$ ${formatMoeda(item.valor_total)}</span>
                            </div>
                            ${detailsListHtml}
                        </div>
                    `;
                    memWrapper.appendChild(card);
                });
            } else {
                memWrapper.innerHTML = `<div class="alert-info-box"><i class="fa-solid fa-circle-question"></i><p>Nenhuma memória de cálculo gerada.</p></div>`;
            }
        });
}

function toggleAccordion(header) {
    const body = header.nextElementSibling;
    const icon = header.querySelector("i");
    
    if (body.style.display === "none") {
        body.style.display = "flex";
        icon.className = "fa-solid fa-chevron-up text-muted";
    } else {
        body.style.display = "none";
        icon.className = "fa-solid fa-chevron-down text-muted";
    }
}

// ==========================================
// UTILITY HELPER FUNCTIONS
// ==========================================

function formatMoeda(val) {
    if (val === undefined || val === null) return "0,00";
    return val.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function applyCNPJMask(input) {
    let value = input.value.replace(/\D/g, "");
    
    if (value.length > 14) {
        value = value.substring(0, 14);
    }
    
    if (value.length > 12) {
        input.value = `${value.substring(0, 2)}.${value.substring(2, 5)}.${value.substring(5, 8)}/${value.substring(8, 12)}-${value.substring(12)}`;
    } else if (value.length > 8) {
        input.value = `${value.substring(0, 2)}.${value.substring(2, 5)}.${value.substring(5, 8)}/${value.substring(8)}`;
    } else if (value.length > 5) {
        input.value = `${value.substring(0, 2)}.${value.substring(2, 5)}.${value.substring(5)}`;
    } else if (value.length > 2) {
        input.value = `${value.substring(0, 2)}.${value.substring(2)}`;
    } else {
        input.value = value;
    }
}
