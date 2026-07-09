/**
 * Gerador de Atestes BSF - Lógica de Upload e Download
 */

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileListContainer = document.getElementById('file-list-container');
    const fileList = document.getElementById('file-list');
    const actionContainer = document.getElementById('action-container');
    const btnProcessar = document.getElementById('btn-processar');
    const statusContainer = document.getElementById('status-container');
    const progressBar = document.getElementById('process-progress');
    const statusText = document.getElementById('process-status-text');
    const processLogs = document.getElementById('process-logs');

    let selectedFile = null;

    // Drag and Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        
        // Pegamos apenas o primeiro arquivo (deve ser Excel ou CSV)
        const file = files[0];
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (!['xlsx', 'xls', 'csv'].includes(ext)) {
            Swal.fire({
                icon: 'error',
                title: 'Arquivo inválido',
                text: 'Por favor, selecione um arquivo Excel (.xlsx, .xls) ou CSV.'
            });
            return;
        }

        selectedFile = file;
        
        // Atualizar UI
        fileList.innerHTML = `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-file-excel text-success me-2"></i>
                    <span class="fw-bold">${file.name}</span>
                    <small class="text-muted ms-2">(${(file.size / 1024).toFixed(1)} KB)</small>
                </div>
                <button class="btn btn-sm btn-outline-danger rounded-pill" onclick="window.location.reload()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        fileListContainer.classList.remove('d-none');
        actionContainer.classList.remove('d-none');
        document.getElementById('file-count').textContent = '1';
        
        // Esconder zona de drop se quiser, ou deixar para trocar
        // dropZone.classList.add('d-none');
    }

    btnProcessar.addEventListener('click', async function() {
        if (!selectedFile) return;

        // Preparar UI de progresso
        actionContainer.classList.add('d-none');
        statusContainer.classList.remove('d-none');
        addLog(`Iniciando processamento de: ${selectedFile.name}`);
        
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            updateStatus(20, 'Enviando arquivo para o servidor...');
            
            const response = await fetch('/api/bsf/gerar-atestes', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao processar arquivo.');
            }

            updateStatus(80, 'Gerando documentos e empacotando ZIP...');
            addLog('Sucesso! Recebendo pacote ZIP...');

            // Formato de download do ZIP
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `BSF_Atestes_${new Date().toISOString().split('T')[0]}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            updateStatus(100, 'Concluído com sucesso!');
            addLog('Download iniciado automaticamente.');
            
            Swal.fire({
                icon: 'success',
                title: 'Atestes Gerados!',
                text: 'O download do seu arquivo ZIP foi iniciado.',
                confirmButtonText: 'Ótimo'
            });

        } catch (error) {
            console.error('Erro:', error);
            updateStatus(0, 'Erro no processamento');
            addLog(`ERRO: ${error.message}`, 'text-danger');
            
            Swal.fire({
                icon: 'error',
                title: 'Falha na Geração',
                text: error.message
            });
            
            actionContainer.classList.remove('d-none');
        }
    });

    function updateStatus(percent, text) {
        progressBar.style.width = `${percent}%`;
        statusText.textContent = text;
    }

    function addLog(message, className = '') {
        const div = document.createElement('div');
        div.className = className;
        div.textContent = `> ${message}`;
        processLogs.appendChild(div);
        processLogs.scrollTop = processLogs.scrollHeight;
    }
});
