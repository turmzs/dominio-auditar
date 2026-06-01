// Architecture Menu - Sistema de menu em cascata com estrutura modular

let menuStructure = null;

// Fases de implementação (fonte de verdade vem do backend também)
let implementationPhases = null;

// Inicializar quando DOM está pronto
document.addEventListener('DOMContentLoaded', function () {
    initArchitecture().catch(() => {
        // Fallback simples
        const body = document.getElementById('module-body');
        if (body) {
            body.innerHTML = `
        <div class="welcome-screen">
          <h3>Falha ao carregar arquitetura</h3>
          <p>Não foi possível buscar /api/architecture.</p>
        </div>
      `;
        }
    });
});

async function initArchitecture() {
    const resp = await fetch('/api/architecture', { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!resp.ok) throw new Error('Falha ao buscar /api/architecture');

    const data = await resp.json();
    menuStructure = data.architecture;
    implementationPhases = data.implementation_phases;

    buildMenu();
    renderPhases();
    attachEventListeners();
}

// Construir menu em cascata
function buildMenu() {
    const container = document.getElementById('menu-container');
    if (!container) return;

    container.innerHTML = '';

    menuStructure.forEach(module => {
        const button = document.createElement('button');
        button.className = 'menu-button';
        button.innerHTML = module.label;
        button.dataset.id = module.id;
        button.dataset.etapa = module.etapa || 'N/A';

        button.addEventListener('click', function (e) {
            e.stopPropagation();
            toggleDropdown(this);
        });

        const dropdown = document.createElement('div');
        dropdown.className = 'dropdown-menu';
        dropdown.id = 'dropdown-' + module.id;

        // Submenus vindos do backend: módulo->submenus
        const submenus = module.submenus || [];
        submenus.forEach(submenu => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';

            // compatibilidade: frontend anterior usava `items`
            const submenuItems = submenu.items || submenu.submenus || [];
            if (submenuItems && submenuItems.length > 0) item.classList.add('has-submenu');

            item.innerHTML = submenu.label;
            item.dataset.id = submenu.id;

            if (submenuItems && submenuItems.length > 0) {
                item.addEventListener('mouseenter', function () {
                    showSubmenu(this, submenuItems, submenu.label);
                });
            } else {
                item.addEventListener('click', function () {
                    loadModule(submenu.id, submenu.label, submenu.route);
                    closeAllDropdowns();
                });
            }

            dropdown.appendChild(item);
        });

        button.parentNode ? button.parentNode.insertBefore(dropdown, button.nextSibling) : null;
        container.appendChild(button);
        container.appendChild(dropdown);
    });
}

// Toggle dropdown
function toggleDropdown(button) {
    const dropdown = button.nextElementSibling;
    const isVisible = dropdown && dropdown.classList.contains('visible');

    closeAllDropdowns();

    if (!isVisible) {
        if (dropdown) dropdown.classList.add('visible');
        button.classList.add('active');
    }
}

// Fechar todos os dropdowns
function closeAllDropdowns() {
    document.querySelectorAll('.dropdown-menu.visible').forEach(menu => {
        menu.classList.remove('visible');
    });
    document.querySelectorAll('.menu-button.active').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.submenu.visible').forEach(sub => {
        sub.classList.remove('visible');
    });
}

// Mostrar submenu
function showSubmenu(item, items, parentLabel) {
    let submenu = item.querySelector('.submenu');

    if (!submenu) {
        submenu = document.createElement('div');
        submenu.className = 'submenu';

        items.forEach(subitem => {
            const link = document.createElement('div');
            link.className = 'submenu-item';
            link.innerHTML = subitem.label;
            link.addEventListener('click', function () {
                loadModule(subitem.id, subitem.label, subitem.route, parentLabel);
                closeAllDropdowns();
            });
            submenu.appendChild(link);
        });

        item.appendChild(submenu);
    }

    submenu.classList.add('visible');
}

// Carregar módulo
function loadModule(moduleId, moduleName, route, parentName = '') {
    const title = parentName ? `${parentName} > ${moduleName}` : moduleName;

    const titleEl = document.getElementById('module-title');
    if (titleEl) titleEl.textContent = title;

    // Atualizar breadcrumb
    const breadcrumb = document.getElementById('breadcrumb-trail');
    if (breadcrumb) {
        breadcrumb.innerHTML = `<span class="breadcrumb-item">Home</span><span class="breadcrumb-item">${title}</span>`;
    }

    // Buscar status do módulo (placeholder agora, mas já habilita evolução)
    fetch(`/api/modules/${encodeURIComponent(moduleId)}/status`, { method: 'GET', headers: { 'Accept': 'application/json' } })
        .then(r => r.ok ? r.json() : Promise.reject(new Error('status inválido')))
        .then(meta => {
            const body = document.getElementById('module-body');
            if (!body) return;

            const etapa = meta.etapa ?? 'N/A';
            const status = meta.status ?? 'em_desenvolvimento';

            body.innerHTML = `
        <div class="module-placeholder">
          <h3>${meta.label || moduleName}</h3>
          <p>Módulo em desenvolvimento...</p>
          <div class="route-info">
            <strong>Route:</strong> ${meta.route || route || '-'}<br/>
            <strong>ID:</strong> ${meta.module_id || moduleId}<br/>
            <strong>ETAPA:</strong> ${etapa}<br/>
            <strong>Status:</strong> ${status}<br/>
          </div>
        </div>
      `;
        })
        .catch(() => {
            const body = document.getElementById('module-body');
            if (!body) return;
            body.innerHTML = `
        <div class="module-placeholder">
          <h3>${moduleName}</h3>
          <p>Módulo em desenvolvimento...</p>
          <div class="route-info">
            <strong>Route:</strong> ${route}<br/>
            <strong>ID:</strong> ${moduleId}
          </div>
        </div>
      `;
        });
}

// Renderizar fases
function renderPhases() {
    const grid = document.getElementById('phases-grid');
    if (!grid || !implementationPhases) return;

    grid.innerHTML = '';

    implementationPhases.forEach(phase => {
        const card = document.createElement('div');
        card.className = 'phase-card';
        card.innerHTML = `
      <h5><span class="etapa-badge">ETAPA ${phase.etapa}</span>${phase.nome}</h5>
      <p>${phase.modulos.join(', ')}</p>
    `;
        grid.appendChild(card);
    });
}

// Anexar event listeners globais
function attachEventListeners() {
    // Fechar menus ao clicar fora
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.menu-button') && !e.target.closest('.dropdown-menu')) {
            closeAllDropdowns();
        }
    });

    // Fechar submenu ao sair
    document.addEventListener('mouseleave', function () {
        document.querySelectorAll('.submenu.visible').forEach(sub => {
            sub.classList.remove('visible');
        });
    }, true);
}

