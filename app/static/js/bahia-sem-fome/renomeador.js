
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

        // Feedback visual e travamento do sistema
        statusContainer.classList.remove('d-none');
        btnProcessar.disabled = true;
        dropZone.style.pointerEvents = 'none';
        dropZone.style.opacity = '0.5';
        
        // Esconde botões de exclusão na lista para evitar alteração durante o processamento
        document.querySelectorAll('#file-list button').forEach(btn => btn.style.display = 'none');
        
        progressBar.style.width = '0%';
        progressBar.classList.add('progress-bar-striped', 'progress-bar-animated');
        statusText.textContent = 'Iniciando processamento em lote...';
        addLog(`Iniciando processamento sequencial de ${selectedFiles.length} arquivos...`);

        // Cria a instância do JSZip para agrupar tudo no navegador
        const zip = new JSZip();
        let arquivosComSucesso = 0;

        try {
            for (let i = 0; i < selectedFiles.length; i++) {
                const file = selectedFiles[i];
                const indexUmBase = i + 1;
                
                statusText.textContent = `Processando arquivo ${indexUmBase} de ${selectedFiles.length}...`;
                addLog(`Enviando [${file.name}] (${(file.size / 1024).toFixed(1)} KB) para a IA...`);

                // Atualiza barra de progresso antes de iniciar
                const baseProgress = (i / selectedFiles.length) * 100;
                progressBar.style.width = `${baseProgress}%`;

                // Monta FormData apenas com o arquivo individual
                const formData = new FormData();
                formData.append('file', file);

                let novoNome = file.name;
                try {
                    const response = await fetch('/api/bahia-sem-fome/renomeador-individual', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        novoNome = data.new_name || file.name;
                        addLog(`✅ Sucesso [${file.name}] -> Renomeado para: ${novoNome}`);
                        arquivosComSucesso++;
                    } else {
                        // Trata erros não-JSON (como 413, 502, 504, 500 etc.)
                        let errorMessage = `Erro ${response.status}: ${response.statusText}`;
                        try {
                            const contentType = response.headers.get("content-type");
                            if (contentType && contentType.includes("application/json")) {
                                const errorData = await response.json();
                                errorMessage = errorData.detail || errorMessage;
                            } else {
                                const textData = await response.text();
                                errorMessage = textData || errorMessage;
                            }
                        } catch (e) {}
                        addLog(`⚠️ Falha ao processar [${file.name}]: ${errorMessage}. Mantendo nome original.`);
                    }
                } catch (err) {
                    addLog(`⚠️ Erro de rede no arquivo [${file.name}]: ${err.message}. Mantendo nome original.`);
                }

                // Adiciona o arquivo no ZIP com o novo nome
                zip.file(novoNome, file);
                
                // Incrementa progresso após a conclusão do arquivo
                const progressConcluido = (indexUmBase / selectedFiles.length) * 100;
                progressBar.style.width = `${progressConcluido}%`;
            }

            statusText.textContent = 'Gerando arquivo ZIP final...';
            addLog('Empacotando todos os arquivos renomeados no navegador...');
            
            // Gera o ZIP final
            const zipContent = await zip.generateAsync({ type: 'blob' });
            
            // Dispara o download automático do ZIP
            const url = window.URL.createObjectURL(zipContent);
            const a = document.createElement('a');
            a.href = url;
            a.download = `BSF_Renomeados_${new Date().getTime()}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            progressBar.classList.remove('progress-bar-striped', 'progress-bar-animated');
            progressBar.style.width = '100%';
            statusText.textContent = 'Sucesso! Download concluído.';
            addLog(`Processamento concluído. ${arquivosComSucesso} de ${selectedFiles.length} arquivos renomeados.`);
            
            if (window.ui) {
                window.ui.feedbackSucesso(`Lote concluído! ${arquivosComSucesso} arquivos processados com sucesso.`);
            }
            
            setTimeout(() => {
                resetUI();
            }, 3000);

        } catch (error) {
            console.error('Erro crítico no lote:', error);
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
