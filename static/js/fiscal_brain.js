async function handleXmlUpload(input) {
    const file = input.files[0];
    if (!file) return;

    const statusDiv = document.getElementById('upload-status');
    statusDiv.innerHTML = '<i class=\"fa-solid fa-spinner fa-spin\"></i> Processando XML e rodando Cérebro Fiscal...';
    statusDiv.style.color = '#3498db';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/xml/importar', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.status === 'sucesso') {
            statusDiv.innerHTML = '<i class=\"fa-solid fa-check-circle\"></i> Sucesso! Redirecionando para Auditoria...';
            statusDiv.style.color = '#2ecc71';

            setTimeout(() => {
                window.location.href = `/motor_fiscal/audit_results?id=${result.movement_id}`;
            }, 1500);
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        statusDiv.innerHTML = '<i class=\"fa-solid fa-circle-xmark\"></i> Erro: ' + error.message;
        statusDiv.style.color = '#e74c3c';
    }
}

function renderImportPage() {
    const contentArea = document.getElementById('dashboard-content');
    if (!contentArea) return;
    contentArea.innerHTML = `
        <div class=\"dashboard-container\">
            <div class=\"card\" style=\"background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; max-width: 600px; margin: 0 auto;\">
                <i class=\"fa-solid fa-cloud-arrow-up\" style=\"font-size: 3rem; color: #3498db; margin-bottom: 20px;\"></i>
                <h2 style=\"color: #333;\">Importação de XML Fiscal</h2>
                <p style=\"color: #666; margin-bottom: 25px;\">Selecione o arquivo XML da NF-e para análise Fiscal.</p>
                <div class=\"upload-zone\" style=\"border: 2px dashed #ccc; padding: 40px; border-radius: 10px; cursor: pointer;\" onmouseover=\"this.style.borderColor='#3498db'\" onmouseout=\"this.style.borderColor='#ccc'\">
                    <input type=\"file\" id=\"xml-file-input\" style=\"display: none;\" accept=\".xml\" onchange=\"handleXmlUpload(this)\">
                    <label for=\"xml-file-input\" style=\"cursor: pointer;\">
                        <strong style=\"color: #3498db;\">Clique para selecionar ou arraste o arquivo</strong>
                    </label>
                </div>
                <div id=\"upload-status\" style=\"margin-top: 20px; font-weight: 500;\"></div>
            </div>
        </div>
    `;
}

/*
 * IMPORTANTE:
 * Esta aplicação possui duas implementações de UI de importação:
 * - A UI nova (app_new.js) com cascata/abas/lote.
 * - A UI legada (renderImportPage()) interceptada originalmente aqui.
 *
 * Para evitar que a UI legada sobrescreva a UI nova, o intercept foi desabilitado por padrão.
 * Se você quiser usar a UI antiga temporariamente, defina:
 *   window.__USE_LEGACY_IMPORT_UI__ = true;
 */
(function () {
    const originalLoadContent = window.loadContent;
    window.loadContent = function (tabName) {
        if (tabName === 'importacao' && window.__USE_LEGACY_IMPORT_UI__ === true) {
            renderImportPage();
        } else if (typeof originalLoadContent === 'function') {
            originalLoadContent(tabName);
        }
    };
})();
