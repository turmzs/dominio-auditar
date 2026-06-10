/* ============================================
   DOMINIO AUDITAR - UI NEW (fallback-safe)
   Obs: este arquivo foi reconstruído para evitar quebras de sintaxe.
   Objetivo: destravar navegação (switchTab/toggleMenu) e telas de importação/apuração.
   ============================================ */

let activeTab = 'dashboard';

/* ====== Menus ====== */
function toggleMenu(e, menuId) {
    e.preventDefault();
    e.stopPropagation();

    const menu = document.getElementById(menuId);
    if (!menu) return;

    document.querySelectorAll('.dropdown-menu').forEach(m => {
        if (m.id !== menuId) m.classList.remove('show');
    });
    menu.classList.toggle('show');
}

document.addEventListener('click', function (e) {
    if (!e.target.closest('.menu-dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

/* ====== Tabs / Loading ====== */
function switchTab(tabName) {
    activeTab = tabName;
    document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('show'));
    loadContent(tabName);
}

function loadContent(tabName) {
    const contentArea = document.getElementById('dashboard-content');
    if (!contentArea) return;

    switch (tabName) {
        case 'dashboard':
            loadDashboard(contentArea);
            break;
        case 'apuracao':
            loadApuracaoFase4(contentArea);
            break;
        case 'importacao':
            loadImportacao(contentArea);
            break;
        default:
            contentArea.innerHTML = `<div class="dashboard-container" style="padding:20px;">Tab '${String(tabName)}' não implementada.</div>`;
            break;
    }
}

function loadDashboard(contentArea) {
    contentArea.innerHTML = `
        <div class="dashboard-container">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-icon"><i class="fa-solid fa-file-invoice"></i></div>
                    <div class="kpi-content">
                        <div class="kpi-label">Notas Emitidas</div>
                        <div class="kpi-value">—</div>
                        <div class="kpi-subtitle">—</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/* ====== Apuração (Fase 4) ====== */
function loadApuracaoFase4(contentArea) {
    contentArea.innerHTML = `
        <div class="dashboard-container">
            <div class="section-container" style="max-width:980px; margin:0 auto;">
                <div class="section-header" style="display:flex; justify-content:space-between; align-items:flex-end; gap:12px;">
                    <h2 style="margin:0; color: white;">Apuração (Fase 4)</h2>
                    <div class="text-muted" style="font-size:.9rem;">ICMS / PIS / COFINS / Simples</div>
                </div>

                <div style="margin-top:16px; padding:14px; background:#ffffff; border:1px solid #d0dede; border-radius:10px;">
                    <div style="display:flex; flex-wrap:wrap; gap:12px; align-items:flex-end;">
                        <div>
                            <div class="trib-info" style="color: black;">Empresa</div>
                            <select id="apuracao_empresa_id" style="padding:10px; width:230px; border:1px solid #d0dede; border-radius:8px;"></select>
                        </div>
                        <div>
                            <div class="trib-info" style="color: black;">Mês</div>
                            <input id="apuracao_mes" type="number" style="padding:10px; width:120px; border:1px solid #d0dede; border-radius:8px;" value="5" />
                        </div>
                        <div>
                            <div class="trib-info" style="color: black;">Ano</div>
                            <input id="apuracao_ano" type="number" style="padding:10px; width:140px; border:1px solid #d0dede; border-radius:8px;" value="2026" />
                        </div>
                        <div>
                            <div class="trib-info" style="color: black;">Modo</div>
                            <select id="apuracao_imposto" style="padding:10px; width:190px; border:1px solid #d0dede; border-radius:8px;">
                                <option value="SIMPLES" selected>Simples</option>
                                <option value="PRESUMIDO">Presumido</option>
                                <option value="REAL">Real</option>
                            </select>
                        </div>
                        <div style="margin-left:auto;">
                            <button id="apuracao_calcular_btn" class="btn-primary" style="padding:11px 14px; border:none; border-radius:8px; cursor:pointer; background:#1a7171; color:#fff; font-weight:700;">
                                Calcular
                            </button>
                        </div>
                    </div>

                    <div id="apuracao_status" style="margin-top:14px; min-height:22px; font-weight:600; color:#4a6a6a;"></div>
                </div>

                <div style="margin-top:16px; display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:12px;">
                    <div class="stat-card" style="background:#fff; border:1px solid #000000; border-radius:10px; padding:14px;">
                        <div class="label" style="color: black;">Débitos</div>
                        <div class="value" id="apuracao_total_debito" style="color: black;">R$ 0,00</div>
                    </div>
                    <div class="stat-card" style="background:#fff; border:1px solid #000000; border-radius:10px; padding:14px;">
                        <div class="label" style="color: black;">Créditos</div>
                        <div class="value" id="apuracao_total_credito" style="color: black;">R$ 0,00</div>
                    </div>
                    <div class="stat-card" style="background:#fff; border:1px solid #000000; border-radius:10px; padding:14px;">
                        <div class="label" style="color: black;">Saldo</div>
                        <div class="value" id="apuracao_valor_final" style="color: black;">R$ 0,00</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // init + bindings
    (async function init() {
        const selectEl = document.getElementById('apuracao_empresa_id');
        const statusEl = document.getElementById('apuracao_status');
        const btn = document.getElementById('apuracao_calcular_btn');
        if (!selectEl || !statusEl) return;

        try {
            statusEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Carregando empresas...';
            const res = await fetch('/api/empresas');
            const data = await res.json();
            const list = Array.isArray(data) ? data : (data?.empresas || []);

            selectEl.innerHTML = '';
            list.forEach(emp => {
                const opt = document.createElement('option');
                opt.value = emp.id;
                opt.textContent = emp.nome || `Empresa #${emp.id}`;
                selectEl.appendChild(opt);
            });
            statusEl.innerHTML = '';

            if (btn) btn.addEventListener('click', () => window.__apuracao_do_calculo());
            selectEl.addEventListener('change', () => window.__apuracao_do_calculo());

            window.__apuracao_do_calculo = async function () {
                const empresa_id = Number(selectEl.value);
                const mes = Number(document.getElementById('apuracao_mes')?.value || 0);
                const ano = Number(document.getElementById('apuracao_ano')?.value || 0);
                const imposto = String(document.getElementById('apuracao_imposto')?.value || 'ICMS').toUpperCase();

                if (!empresa_id || Number.isNaN(empresa_id)) {
                    statusEl.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Selecione uma empresa válida.';
                    return;
                }
                if (!mes || !ano) {
                    statusEl.textContent = 'Preencha mês e ano.';
                    return;
                }

                if (btn) btn.disabled = true;
                statusEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Calculando apuração...';

                try {
                    const resCalc = await fetch('/apuracao/calcular', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ empresa_id, mes, ano, imposto })
                    });
                    const payload = await resCalc.json();
                    if (!resCalc.ok || payload.status !== 'sucesso') {
                        throw new Error(payload.message || 'Falha ao calcular apuração');
                    }

                    const resumoRes = await fetch(`/apuracao/resumo?empresa_id=${empresa_id}&mes=${mes}&ano=${ano}&imposto=${encodeURIComponent(imposto)}`);
                    const resumo = await resumoRes.json();
                    if (!resumoRes.ok || resumo.status === 'erro') {
                        throw new Error(resumoRes.message || 'Falha ao carregar resumo');
                    }

                    const formatBRL = (n) => (Number(n || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                    document.getElementById('apuracao_total_debito').textContent = formatBRL(resumo.debito);
                    document.getElementById('apuracao_total_credito').textContent = formatBRL(resumo.credito);
                    document.getElementById('apuracao_valor_final').textContent = formatBRL(resumo.final);

                    statusEl.innerHTML = `<i class="fa-solid fa-check-circle"></i> Apuração ${resumo.periodo} (${resumo.imposto}): ${resumo.status}.`;
                } catch (e) {
                    statusEl.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Erro: ${e.message || e}`;
                } finally {
                    if (btn) btn.disabled = false;
                }
            };

            // cálculo automático inicial
            try { await window.__apuracao_do_calculo(); } catch (e) { }
        } catch (e) {
            statusEl.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Erro ao carregar empresas: ${e.message || e}`;
        }
    })();
}

/* ====== Lote resumo (localStorage) ====== */
function renderLoteResumo() {
    const wrap = document.getElementById('lote-resumo-wrap');
    if (!wrap) return;

    let detalhes = [];
    let meta = null;

    try { detalhes = JSON.parse(localStorage.getItem('lastImportBatchDetails') || '[]'); } catch (e) { detalhes = []; }
    try { meta = JSON.parse(localStorage.getItem('lastImportBatchMeta') || 'null'); } catch (e) { meta = null; }

    if (!detalhes || detalhes.length === 0) {
        wrap.innerHTML = `
            <div class="alert-info-box">
                <i class="fa-solid fa-circle-info"></i>
                <p>Nenhum lote encontrado. Importe notas para ver o resumo.</p>
            </div>
        `;
        return;
    }

    const esc = (v) => (v === null || v === undefined) ? '' : String(v).replace(/[&<>"']/g, (m) => ({
        '&': '&amp;', '<': '<', '>': '>', '"': '"', "'": '&#39;'
    }[m]));

    const rows = detalhes.map((r, idx) => {
        const status = r.status || 'erro';
        const badgeClass =
            status === 'sucesso' ? 'badge badge-ok' :
                (status === 'duplicate' || r.duplicate) ? 'badge badge-warning' :
                    'badge badge-alert';

        const movementId = r.movement_id ? Number(r.movement_id) : null;
        const actionHtml = movementId
            ? `<button class="btn-secondary" style="padding:6px 10px;" onclick="window.location.href='/motor_fiscal/resultado/${movementId}'">Auditar</button>`
            : '';

        const msg = r.message ? esc(r.message) : '';

        return `
            <tr>
                <td>${idx + 1}</td>
                <td>${esc(r.filename || r.file || '-')}</td>
                <td><span class="${badgeClass}">${status === 'sucesso' ? 'Sucesso' : (r.duplicate ? 'Duplicate' : 'Erro')}</span></td>
                <td>${movementId ? movementId : '-'}</td>
                <td>${msg || '-'}</td>
                <td>${actionHtml}</td>
            </tr>
        `;
    }).join('');

    const okCount = detalhes.filter(r => r.status === 'sucesso').length;
    const errCount = detalhes.filter(r => r.status !== 'sucesso').length;

    const metaHtml = (meta && typeof meta === 'object')
        ? `<div style="color:#4a6a6a; font-weight:600; margin-bottom:10px;">Total: ${meta.total_arquivos ?? detalhes.length} | Sucessos: ${meta.sucessos ?? okCount} | Erros: ${meta.erros ?? errCount}</div>`
        : '';

    wrap.innerHTML = `
        <div class="section-container" style="padding:0;">
            ${metaHtml}
            <div class="table-responsive">
                <table class="data-table" style="width:100%;">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Arquivo</th>
                            <th>Status</th>
                            <th>movement_id</th>
                            <th>Mensagem</th>
                            <th>Ação</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        </div>
    `;
}

/* ====== Importação em lote ====== */
function loadImportacao(contentArea) {
    contentArea.innerHTML = `
        <div class="dashboard-container">
            <div class="section-container" style="max-width: 980px; margin: 0 auto;">
                <div class="section-header" style="justify-content: space-between;">
                    <h2 style="margin: 0; color: white;">Cérebro Fiscal - Importação em Lote</h2>
                    <div class="text-muted" style="font-size: .9rem;">Envie XML por tipo (Entradas / Serviços / Saídas)</div>
                </div>

                <div class="import-tabs" style="display:flex; gap:12px; border-bottom: 1px solid #e6efef; margin-top: 18px;">
                    <button class="tab-btn active" data-tab="entradas" onclick="switchImportTab('entradas')">Entradas</button>
                    <button class="tab-btn" data-tab="servicos" onclick="switchImportTab('servicos')">Serviços</button>
                    <button class="tab-btn" data-tab="saidas" onclick="switchImportTab('saidas')">Saídas</button>
                </div>

                <div class="import-tab-content" style="padding: 18px 0 6px 0;">
                    <div class="import-pane" id="import-pane-entradas">${renderImportPane('entrada', 'entradas')}</div>
                    <div class="import-pane" id="import-pane-servicos" style="display:none;">${renderImportPane('servico', 'servicos')}</div>
                    <div class="import-pane" id="import-pane-saidas" style="display:none;">${renderImportPane('saida', 'saidas')}</div>
                </div>

                <div id="import-batch-status" style="margin-top: 18px; font-weight: 500;"></div>

                <div style="margin-top: 12px;">
                    <div id="lote-resumo-wrap" style="margin-top: 18px;"></div>
                </div>
            </div>
        </div>
    `;

    try { renderLoteResumo(); } catch (e) { }
}

function renderImportPane(tipoMovimento, tabKey) {
    const safeTipo = String(tipoMovimento || 'entrada');
    const inputId = `xml-file-input-${tabKey}`;
    const statusId = `upload-status-${tabKey}`;

    return `
        <div>
            <div style="margin-bottom:10px; color:#5a7070; font-size:.9rem;">Envie XML (${tabKey}) em lote</div>

            <input type="file" id="${inputId}" multiple accept=".xml" style="margin-bottom:10px;" onchange="handleXmlUploadBatch('${safeTipo}', '${inputId}', false)" />

            <div id="${statusId}" style="min-height:18px; margin-bottom:10px;"></div>

            <button class="btn-primary" onclick="handleXmlUploadBatch('${safeTipo}', '${inputId}', true)" style="padding:10px 14px; border:none; border-radius:8px; cursor:pointer; background:#1a7171; color:#fff; font-weight:700;">
                Importar em lote
            </button>
        </div>
    `;
}

function switchImportTab(tabKey) {
    const ids = {
        entradas: 'import-pane-entradas',
        servicos: 'import-pane-servicos',
        saidas: 'import-pane-saidas'
    };

    Object.values(ids).forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });

    const activeId = ids[tabKey];
    const active = activeId ? document.getElementById(activeId) : null;
    if (active) active.style.display = 'block';

    document.querySelectorAll('.import-tabs .tab-btn').forEach(btn => {
        const isActive = btn.getAttribute('data-tab') === tabKey;
        btn.classList.toggle('active', isActive);
        btn.style.borderBottomColor = isActive ? '#1a7171' : 'transparent';
    });
}

async function handleXmlUploadBatch(tipoMovimento, inputId, importarAgora = false) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const files = Array.from(input.files || []);
    const tabId = inputId.split('xml-file-input-')[1] || '';
    const statusDiv = document.getElementById(`upload-status-${tabId}`);

    if (files.length === 0) {
        if (statusDiv) statusDiv.innerHTML = 'Nenhum arquivo selecionado.';
        return;
    }

    if (!importarAgora) {
        if (statusDiv) statusDiv.innerHTML = `${files.length} arquivo(s) selecionado(s). Clique em "Importar em lote".`;
        return;
    }

    if (statusDiv) {
        statusDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Importando em lote...';
        statusDiv.style.color = '#3498db';
    }

    const formData = new FormData();
    formData.append('origem', 'local');
    formData.append('tipo_movimento', tipoMovimento);
    files.forEach(f => formData.append('files', f));

    try {
        const response = await fetch('/xml/importar', { method: 'POST', body: formData });
        const ct = (response.headers.get('content-type') || '').toLowerCase();

        if (!ct.includes('application/json')) {
            const txt = await response.text();
            throw new Error(`Resposta não-JSON (content-type: ${ct}). Texto inicial: ${txt.slice(0, 200)}`);
        }

        const result = await response.json();

        if (statusDiv) {
            if (result.status === 'concluido') {
                const ok = result.sucessos || 0;
                const er = result.erros || 0;
                statusDiv.innerHTML = `<i class="fa-solid fa-check-circle"></i> Lote finalizado: ${ok} sucesso(s), ${er} erro(s).`;
                statusDiv.style.color = '#2ecc71';
            } else if (result.status === 'sucesso') {
                statusDiv.innerHTML = `<i class="fa-solid fa-check-circle"></i> Importação concluída.`;
                statusDiv.style.color = '#2ecc71';
            } else {
                statusDiv.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Erro: ${result.message || 'Falha ao processar'}`;
                statusDiv.style.color = '#e74c3c';
                return;
            }
        }

        if (result && Array.isArray(result.detalhes)) {
            try {
                localStorage.setItem('lastImportBatchDetails', JSON.stringify(result.detalhes));
                localStorage.setItem('lastImportBatchMeta', JSON.stringify({
                    total_arquivos: result.total_arquivos ?? result.detalhes.length,
                    sucessos: result.sucessos ?? result.detalhes.filter(r => r.status === 'sucesso').length,
                    erros: result.erros ?? result.detalhes.filter(r => r.status !== 'sucesso').length,
                    tipo_movimento: result.tipo_movimento ?? tipoMovimento
                }));
            } catch (e) { }
        }

        setTimeout(() => {
            try { renderLoteResumo(); } catch (e) { }
        }, 150);

        setTimeout(() => {
            try { switchTab('apuracao'); } catch (e) { }
        }, 300);

    } catch (e) {
        if (statusDiv) {
            statusDiv.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Erro: ${e.message || e}`;
            statusDiv.style.color = '#e74c3c';
        }
    }
}

// garante handlers globais (caso template chame por onclick)
window.switchTab = switchTab;
window.toggleMenu = toggleMenu;
window.switchImportTab = switchImportTab;
window.handleXmlUploadBatch = handleXmlUploadBatch;
window.renderImportPane = renderImportPane;
window.renderLoteResumo = renderLoteResumo;


