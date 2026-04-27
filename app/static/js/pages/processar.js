document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const resultsGrid = document.getElementById('resultsGrid');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    // --- Drag & Drop Events ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('drag-active'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('drag-active'), false);
    });

    dropzone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length === 0) return;
        uploadFiles(files);
    }

    async function uploadFiles(files) {
        progressContainer.classList.remove('d-none');
        let completed = 0;
        const total = files.length;

        updateProgress(0);

        for (const file of files) {
            // Create a placeholder card immediately
            const tempId = 'card-' + Math.random().toString(36).substr(2, 9);
            createProcessingCard(file, tempId);

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/ocr/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Erro no upload");

                const data = await response.json();

                // Update Card with Success
                updateCardSuccess(tempId, data, file);

            } catch (error) {
                console.error(error);
                updateCardError(tempId, error.message);
            }

            completed++;
            updateProgress((completed / total) * 100);
        }

        // Hide progress after short delay if 100%
        setTimeout(() => {
            if (completed === total) {
                progressText.textContent = "Concluído!";
            }
        }, 1000);
    }

    function updateProgress(percent) {
        const p = Math.round(percent);
        if (progressBar) progressBar.style.width = `${p}%`;
        if (progressText) progressText.textContent = `${p}%`;
    }

    // --- Card Generation Helpers ---

    function createProcessingCard(file, id) {
        const isImage = file.type.startsWith('image/');
        const thumbUrl = isImage ? URL.createObjectURL(file) : null;
        const iconHtml = isImage ? `<img src="${thumbUrl}" alt="Thumb">` : `<i class="bi bi-file-earmark-pdf fs-1 text-muted"></i>`;

        const html = `
            <div id="${id}" class="result-card">
                <div class="card-thumb">
                    ${iconHtml}
                </div>
                <div class="card-content">
                    <h6 class="text-truncate" title="${file.name}">${file.name}</h6>
                    <div class="d-flex align-items-center mt-3 text-muted">
                         <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                         <small>Lendo...</small>
                    </div>
                </div>
            </div>
        `;
        resultsGrid.insertAdjacentHTML('afterbegin', html);
    }

    function updateCardSuccess(id, data, file) {
        const card = document.getElementById(id);
        if (!card) return;

        // Extract meaningful fields if present
        const nome = data.nome_completo || data.nome || "Não identificado";
        const cpf = data.cpf || "---";

        card.innerHTML = `
            <div class="card-thumb position-relative">
                 ${file.type.startsWith('image/') ? `<img src="${URL.createObjectURL(file)}" alt="Thumb">` : `<i class="bi bi-file-earmark-pdf fs-1 text-primary"></i>`}
                 <span class="position-absolute top-0 end-0 m-2 badge bg-success status-badge"><i class="bi bi-check-lg"></i> OK</span>
            </div>
            <div class="card-content">
                <div class="mb-2">
                    <small class="text-muted d-block text-uppercase" style="font-size:0.7em; letter-spacing:1px;">Beneficiário</small>
                    <span class="fw-bold text-dark d-block text-truncate">${nome}</span>
                </div>
                <div class="mb-3">
                    <small class="text-muted d-block text-uppercase" style="font-size:0.7em; letter-spacing:1px;">CPF</small>
                    <span class="font-monospace">${cpf}</span>
                </div>
                
                <a href="/fila-validacao" class="btn btn-sm btn-light w-100 text-primary fw-bold" target="_blank">
                    <i class="bi bi-eye me-1"></i> Validar
                </a>
            </div>
        `;
    }

    function updateCardError(id, msg) {
        const card = document.getElementById(id);
        if (!card) return;

        card.innerHTML = `
            <div class="card-thumb bg-danger-subtle">
                 <i class="bi bi-exclamation-triangle fs-1 text-danger"></i>
            </div>
            <div class="card-content">
                <h6 class="text-danger fw-bold">Falha no Processamento</h6>
                <p class="small text-muted mb-0">${msg}</p>
            </div>
        `;
    }

});
