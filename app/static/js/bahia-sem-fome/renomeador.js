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
    let pollingInterval = null;

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
        const newFiles = Array.from(files).filter(file => {
            return file.type === 'application/pdf' || file.type.startsWith('image/');
        });
        
        if (newFiles.length < files.length) {
            if (window.ui) window.ui.feedbackAviso('Apenas arquivos PDF ou Imagens (PNG/JPG) são aceitos.');
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
                
                let iconClass = 'far fa-file-alt';
                let iconColor = 'text-secondary';
                if (file.type === 'application/pdf') {
                    iconClass = 'far fa-file-pdf';
                    iconColor = 'text-danger';
                } else if (file.type.startsWith('image/')) {
                    iconClass = 'far fa-image';
                    iconColor = 'text-primary';
                }
                
                item.innerHTML = `
                    <div class="text-truncate" style="max-width: 80%;">
                        <i class="${iconClass} ${iconColor} me-2"></i>
                        <span class="small fw-bold">${file.name}</span>
                        <span class="text-muted smaller ms-2">(${(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button class="btn btn-link btn-sm text-danger p-0 hover-lift" onclick="window.removeFile(${index})">
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

    function addLog(message, type = 'info') {
        const time = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        
        let colorClass = 'text-light';
        if (type === 'success') colorClass = 'text-success fw-bold';
        if (type === 'warning') colorClass = 'text-warning';
        if (type === 'danger') colorClass = 'text-danger fw-bold';
        
        logEntry.innerHTML = `<span class="text-muted">[${time}]</span> <span class="${colorClass}">${message}</span>`;
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    btnProcessar.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        // Feedback visual
        statusContainer.classList.remove('d-none');
        btnProcessar.disabled = true;
        dropZone.style.pointerEvents = 'none';
        dropZone.style.opacity = '0.5';
        
        // Esconde botões de exclusão
        document.querySelectorAll('#file-list button').forEach(btn => btn.style.display = 'none');
        
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-primary fw-bold d-flex align-items-center justify-content-center';
        
        statusText.textContent = 'Enviando arquivos para a Fila Inteligente...';
        addLog(`Iniciando envio de ${selectedFiles.length} arquivos para o Piloto Automático...`);

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        // Opcional: Se precisar de tipo_documento, pode enviar 'AUTO'
        formData.append('tipo_documento', 'AUTO');

        try {
            // Faremos o envio e não esperamos o bloqueio, caso o backend segure a conexão,
            // usaremos um fetch normal. Se o endpoint já devolve logo um task_id e processa em background:
            const response = await fetch('/api/bahia-sem-fome/scanner/organizar-lote-upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // A requisição inicial foi aceita
                addLog('✅ Arquivos enviados com sucesso! A IA já está trabalhando...', 'success');
                statusText.textContent = 'Processamento em andamento...';
                
                // Inicia o polling a cada 3 segundos
                iniciarPolling();
            } else {
                const data = await response.json().catch(() => ({}));
                const msg = data.detail || data.mensagem || 'Falha ao enviar arquivos.';
                throw new Error(msg);
            }
        } catch (error) {
            handleError(error.message);
        }
    });
    
    function handleError(msg) {
        statusText.textContent = 'Falha no processamento';
        statusText.className = 'text-center fw-bold text-danger mb-3';
        addLog(`ERRO: ${msg}`, 'danger');
        if (window.ui) window.ui.feedbackErro(msg);
        
        btnProcessar.disabled = false;
        dropZone.style.pointerEvents = 'auto';
        dropZone.style.opacity = '1';
        document.querySelectorAll('#file-list button').forEach(btn => btn.style.display = 'block');
        
        progressBar.className = 'progress-bar bg-danger fw-bold';
        
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }

    function iniciarPolling() {
        if (pollingInterval) clearInterval(pollingInterval);
        
        // Vamos checar imediatamente e depois a cada 3s
        verificarStatusFila();
        pollingInterval = setInterval(verificarStatusFila, 3000);
    }

    async function verificarStatusFila() {
        try {
            const res = await fetch('/api/bahia-sem-fome/scanner/status-fila');
            if (!res.ok) {
                addLog('⚠️ Não foi possível obter o status da fila no momento.', 'warning');
                return;
            }
            
            const data = await res.json();
            /* Esperamos algo como:
               { 
                 status: 'concluido' | 'processando' | 'vazio', 
                 progresso: 100,
                 processados: 5,
                 total: 5,
                 mensagens: ['Log 1', 'Log 2'] 
               }
            */
            
            const p = data.progresso || 0;
            progressBar.style.width = `${p}%`;
            progressBar.textContent = `${p}%`;
            
            if (data.mensagens && Array.isArray(data.mensagens)) {
                data.mensagens.forEach(m => addLog(`🤖 ${m}`));
            }
            
            if (data.status === 'processando') {
                statusText.textContent = `Processando: ${data.processados || 0} de ${data.total || '?'} concluídos...`;
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-success fw-bold d-flex align-items-center justify-content-center';
            } 
            else if (data.status === 'concluido' || p >= 100 || data.status === 'vazio') {
                clearInterval(pollingInterval);
                pollingInterval = null;
                
                progressBar.className = 'progress-bar bg-success fw-bold d-flex align-items-center justify-content-center';
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
                
                if (data.status === 'vazio' && p === 0) {
                    statusText.textContent = 'Processamento Interrompido ou Fila Vazia';
                    statusText.className = 'text-center fw-bold text-warning mb-3';
                } else {
                    statusText.textContent = 'Piloto Automático Finalizado!';
                    statusText.className = 'text-center fw-bold text-success mb-3';
                    addLog('✨ Todos os arquivos foram organizados e renomeados com sucesso!', 'success');
                    if (window.ui) window.ui.feedbackSucesso('Processamento do lote finalizado com sucesso!');
                }
                
                // Limpar interface após um tempo
                setTimeout(() => {
                    resetUI();
                }, 5000);
            }
        } catch (err) {
            console.error('Erro no polling:', err);
        }
    }

    function resetUI() {
        selectedFiles = [];
        updateFileList();
        
        btnProcessar.disabled = false;
        dropZone.style.pointerEvents = 'auto';
        dropZone.style.opacity = '1';
        
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        
        statusText.textContent = 'Aguardando novos arquivos...';
        statusText.className = 'text-center fw-bold text-primary mb-3';
        
        statusContainer.classList.add('d-none');
        logsContainer.innerHTML = '<div class="text-success">> Piloto Automático pronto para a próxima remessa.</div>';
    }

    // Funcionalidade de Scanner Físico integrada ao Piloto Automático
    window.iniciarScannerFisico = async () => {
        statusContainer.classList.remove('d-none');
        btnProcessar.disabled = true;
        dropZone.style.pointerEvents = 'none';
        dropZone.style.opacity = '0.5';
        
        document.querySelectorAll('#file-list button').forEach(btn => btn.style.display = 'none');
        
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-warning text-dark fw-bold d-flex align-items-center justify-content-center';
        
        statusText.textContent = 'Acionando Scanner Físico...';
        addLog(`⏳ Ligando os motores do scanner... Coloque as folhas e aguarde a digitalização.`, 'warning');

        try {
            const response = await fetch('/api/bahia-sem-fome/scanner/escanear-auto-ia', {
                method: 'POST'
            });

            if (response.ok) {
                const data = await response.json().catch(() => ({}));
                
                if (data.status === 'sucesso_sincrono') {
                    // Processamento único imediato (Sem usar a fila)
                    progressBar.style.width = '100%';
                    progressBar.textContent = '100%';
                    progressBar.className = 'progress-bar bg-success fw-bold d-flex align-items-center justify-content-center';
                    
                    statusText.textContent = 'Processamento Finalizado!';
                    statusText.className = 'text-center fw-bold text-success mb-3';
                    
                    addLog('🤖 ' + data.mensagem);
                    addLog('✨ A folha foi processada e organizada imediatamente!', 'success');
                    
                    if (window.ui) window.ui.feedbackSucesso('Folha digitalizada e processada com sucesso!');
                    
                    setTimeout(() => {
                        resetUI();
                    }, 5000);
                } else {
                    // Modo Lote (Mais de 1 folha), vai pra fila
                    addLog('✅ Folhas escaneadas e enviadas à Fila Inteligente!', 'success');
                    statusText.textContent = 'Processamento em andamento...';
                    iniciarPolling();
                }
            } else {
                const data = await response.json().catch(() => ({}));
                const msg = data.detail || data.mensagem || 'Falha ao se comunicar com o scanner.';
                throw new Error(msg);
            }
        } catch (error) {
            handleError(error.message);
        }
    };
});
