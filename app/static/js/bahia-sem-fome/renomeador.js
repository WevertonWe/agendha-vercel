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
    let activeMode = null; // 'ateste' ou 'colletum'

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

    window.selectMode = (mode) => {
        activeMode = mode;
        const selectionContainer = document.getElementById('mode-selection-container');
        const workContainer = document.getElementById('renomeador-work-container');
        const activeBadge = document.getElementById('active-mode-badge');
        const uploadIcon = document.getElementById('upload-icon-mode');

        if (mode === 'ateste') {
            activeBadge.className = 'badge bg-primary p-2 rounded-pill shadow-sm';
            activeBadge.textContent = 'Modo: Ateste Escaneado';
            uploadIcon.className = 'fas fa-file-signature display-1 text-primary mb-3';
        } else {
            activeBadge.className = 'badge bg-success p-2 rounded-pill shadow-sm';
            activeBadge.textContent = 'Modo: Colletum';
            uploadIcon.className = 'fas fa-mobile-alt display-1 text-success mb-3';
        }

        selectionContainer.classList.add('d-none');
        workContainer.classList.remove('d-none');
        addLog(`Modo selecionado: ${mode === 'ateste' ? 'Ateste Escaneado' : 'Colletum'}`);
    };

    window.resetSelection = () => {
        activeMode = null;
        selectedFiles = [];
        updateFileList();
        
        const selectionContainer = document.getElementById('mode-selection-container');
        const workContainer = document.getElementById('renomeador-work-container');
        
        workContainer.classList.add('d-none');
        selectionContainer.classList.remove('d-none');
        
        statusContainer.classList.add('d-none');
        progressBar.style.width = '0%';
        logsContainer.innerHTML = '<div>> Aguardando início do processo...</div>';
    };

    btnProcessar.addEventListener('click', async () => {
        if (selectedFiles.length === 0 || !activeMode) return;

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
        addLog(`Iniciando processamento sequencial de ${selectedFiles.length} arquivos no modo [${activeMode.toUpperCase()}]...`);

        // Cria a instância do JSZip para agrupar tudo no navegador
        const zip = new JSZip();
        let arquivosComSucesso = 0;
        const extractedDataList = [];

        try {
            for (let i = 0; i < selectedFiles.length; i++) {
                const file = selectedFiles[i];
                const indexUmBase = i + 1;
                
                // Intervalo de segurança para evitar Rate Limit (429) no plano gratuito do Gemini
                if (i > 0) {
                    statusText.textContent = `Aguardando intervalo de segurança...`;
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
                
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
                    const response = await fetch(`/api/bahia-sem-fome/renomeador-individual?mode=${activeMode}`, {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        novoNome = data.new_name || file.name;
                        addLog(`✅ Sucesso [${file.name}] -> Renomeado para: ${novoNome}`);
                        arquivosComSucesso++;

                        // Coleta metadados se for ateste para preencher a folha no final
                        if (activeMode === 'ateste' && data.data) {
                            extractedDataList.push(data.data);
                        }
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

            // GERAÇÃO DA FOLHA DE RECEBIMENTO (.DOCX) - Apenas para Atestes
            if (activeMode === 'ateste' && extractedDataList.length > 0) {
                statusText.textContent = 'Gerando ficha de recebimento (.docx)...';
                addLog(`Enviando dados de ${extractedDataList.length} atestes para preencher a folha de recebimento...`);

                try {
                    const docxResponse = await fetch('/api/bahia-sem-fome/gerar-ficha-recebimento', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ items: extractedDataList })
                    });

                    if (docxResponse.ok) {
                        const docxBlob = await docxResponse.blob();
                        // Adiciona a folha preenchida ao ZIP
                        zip.file("Recebimento de documento.docx", docxBlob);
                        addLog('✅ Ficha "Recebimento de documento.docx" gerada e incluída no ZIP com sucesso!');
                    } else {
                        addLog('⚠️ Falha ao gerar ficha de recebimento (servidor retornou erro). O ZIP continuará apenas com os PDFs.');
                    }
                } catch (errDocx) {
                    addLog(`⚠️ Erro ao requisitar geração da ficha de recebimento: ${errDocx.message}. O ZIP continuará apenas com os PDFs.`);
                }
            }

            statusText.textContent = 'Gerando arquivo ZIP final...';
            addLog('Empacotando todos os arquivos renomeados no navegador...');
            
            // Gera o ZIP final
            const zipContent = await zip.generateAsync({ type: 'blob' });
            
            // Dispara o download automático do ZIP
            const url = window.URL.createObjectURL(zipContent);
            const a = document.createElement('a');
            a.href = url;
            a.download = `BSF_${activeMode.toUpperCase()}_Renomeados_${new Date().getTime()}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            progressBar.classList.remove('progress-bar-striped', 'progress-bar-animated');
            progressBar.style.width = '100%';
            statusText.textContent = 'Sucesso! Download concluído.';
            addLog(`Processamento concluído. ${arquivosComSucesso} de ${selectedFiles.length} arquivos processados.`);
            
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
        
        // Remove os logs e barra para a tela inicial do modo
        progressBar.style.width = '0%';
        statusText.textContent = 'Aguardando arquivos...';
        logsContainer.innerHTML = '<div>> Aguardando início do processo...</div>';
        statusContainer.classList.add('d-none');
    }
});
