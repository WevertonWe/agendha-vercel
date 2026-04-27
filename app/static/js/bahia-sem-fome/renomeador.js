
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileListContainer = document.getElementById('file-list-container');
    const fileList = document.getElementById('file-list');
    const fileCount = document.getElementById('file-count');
    const actionContainer = document.getElementById('action-container');
    const btnProcessar = document.getElementById('btn-processar');
    const statusContainer = document.getElementById('status-container');
    const progressBar = document.getElementById('process-progress');
    const statusText = document.getElementById('process-status-text');
    const logsContainer = document.getElementById('process-logs');

    let selectedFiles = [];

    // Drag and Drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        const newFiles = Array.from(files).filter(file => file.type === 'application/pdf');
        
        if (newFiles.length < files.length) {
            if (window.ui) window.ui.feedbackAviso('Apenas arquivos PDF são aceitos.');
        }

        selectedFiles = [...selectedFiles, ...newFiles];
        updateFileList();
    }

    function updateFileList() {
        fileList.innerHTML = '';
        fileCount.textContent = selectedFiles.length;

        if (selectedFiles.length > 0) {
            fileListContainer.classList.remove('d-none');
            actionContainer.classList.remove('d-none');
            
            selectedFiles.forEach((file, index) => {
                const item = document.createElement('div');
                item.className = 'list-group-item d-flex justify-content-between align-items-center py-2';
                item.innerHTML = `
                    <div class="text-truncate" style="max-width: 80%;">
                        <i class="far fa-file-pdf text-danger me-2"></i>
                        <span class="small">${file.name}</span>
                        <span class="text-muted smaller ms-2">(${(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button class="btn btn-link btn-sm text-danger p-0" onclick="window.removeFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                fileList.appendChild(item);
            });
        } else {
            fileListContainer.classList.add('d-none');
            actionContainer.classList.add('d-none');
        }
    }

    window.removeFile = (index) => {
        selectedFiles.splice(index, 1);
        updateFileList();
    };

    btnProcessar.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        // Visual feedback
        statusContainer.classList.remove('d-none');
        btnProcessar.disabled = true;
        dropZone.style.pointerEvents = 'none';
        dropZone.style.opacity = '0.5';
        
        progressBar.style.width = '0%';
        statusText.textContent = 'Enviando arquivos...';
        addLog(`Iniciando envio de ${selectedFiles.length} arquivos.`);

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            addLog('Conectando ao servidor e processando com IA...');
            
            // Simular progresso enquanto espera o servidor (que pode demorar devido à IA)
            let progress = 0;
            const progressInterval = setInterval(() => {
                if (progress < 90) {
                    progress += 1;
                    progressBar.style.width = `${progress}%`;
                    if (progress === 30) statusText.textContent = 'IA analisando conteúdos...';
                    if (progress === 60) statusText.textContent = 'Identificando beneficiários...';
                    if (progress === 85) statusText.textContent = 'Gerando pacote ZIP...';
                }
            }, 500);

            const response = await fetch('/api/bahia-sem-fome/renomeador-lote', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);

            if (response.ok) {
                progressBar.style.width = '100%';
                statusText.textContent = 'Sucesso! Download iniciado.';
                addLog('Processamento concluído com sucesso.');
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `BSF_Renomeados_${new Date().getTime()}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();

                if (window.ui) window.ui.feedbackSucesso('Arquivos processados e pacote baixado!');
                
                resetUI();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao processar arquivos.');
            }
        } catch (error) {
            console.error('Erro:', error);
            statusText.textContent = 'Falha no processamento';
            statusText.classList.replace('text-primary', 'text-danger');
            addLog(`ERRO: ${error.message}`);
            if (window.ui) window.ui.feedbackErro(error.message);
            btnProcessar.disabled = false;
        } finally {
            dropZone.style.pointerEvents = 'auto';
            dropZone.style.opacity = '1';
        }
    });

    function addLog(message) {
        const time = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.innerHTML = `<span class="text-success">[${time}]</span> ${message}`;
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function resetUI() {
        selectedFiles = [];
        updateFileList();
        btnProcessar.disabled = false;
        // Keep status visible for a few seconds then hide or let user close
        setTimeout(() => {
            // statusContainer.classList.add('d-none');
            // progressBar.style.width = '0%';
        }, 5000);
    }
});
