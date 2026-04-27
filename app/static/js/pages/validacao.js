document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('form-validacao');
    const iframeDocumento = document.getElementById('imagem-documento');
    const itemIdInput = document.getElementById('item_id');

    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');

    if (!itemId) {
        alert("ID do item não encontrado. A redirecionar para a fila de validação.");
        window.location.href = '/fila-validacao';
        return;
    }

    async function carregarDadosDoItem() {
        try {
            // Updated URL to correct endpoint
            const response = await fetchWithAuth(`/api/ocr/fila-validacao/${itemId}`);
            if (!response.ok) {
                throw new Error('Falha ao buscar os dados do item para validação.');
            }
            const item = await response.json();

            console.log("Dados recebidos da API:", item);

            // Handle data extraction robustly
            // The structure in store.py is flat: item['dados_extraidos']
            // But previous code expected JSON string in 'dados_extraidos_json'
            // We need to handle both just in case, but store.py saves a dict.
            let dadosOcr = item.dados_extraidos || {};
            if (typeof dadosOcr === 'string') {
                try {
                    const parsed = JSON.parse(dadosOcr);
                    dadosOcr = parsed.dados_extraidos || parsed;
                } catch (e) {
                    console.error("Erro parsing JSON dados_extraidos", e);
                }
            }

            const nomeRealDoFicheiro = item.caminho_arquivo_local.split(/[\\/]/).pop();
            const fileUrl = `/uploads/${nomeRealDoFicheiro}`;

            // Logic to handle PDF vs Image
            const isPdf = nomeRealDoFicheiro.toLowerCase().endsWith('.pdf');
            const container = iframeDocumento.parentElement; // Assuming container for replacement

            if (isPdf) {
                // If it's an iframe, just set src. If it was an img tag, we might need to replace it or just accept iframe usage.
                // The HTML usually has an iframe or div. Let's assume iframeDocumento is an iframe or img element.
                // Best practice: Clear container and append correct element.

                // However, preserving existing element ID logic:
                if (iframeDocumento.tagName === 'IMG') {
                    // Replace IMG with IFRAME
                    const iframe = document.createElement('iframe');
                    iframe.id = 'imagem-documento';
                    iframe.className = 'w-100 h-100 border rounded';
                    iframe.style.minHeight = '600px';
                    iframe.src = fileUrl;
                    iframeDocumento.replaceWith(iframe);
                } else {
                    iframeDocumento.src = fileUrl;
                }
            } else {
                // It is an image
                if (iframeDocumento.tagName === 'IFRAME') {
                    // Replace IFRAME with IMG
                    const img = document.createElement('img');
                    img.id = 'imagem-documento';
                    img.className = 'img-fluid border rounded';
                    img.src = fileUrl;
                    iframeDocumento.replaceWith(img);
                } else {
                    iframeDocumento.src = fileUrl;
                }
            }

            // Preenche todos os campos do formulário com os dados do OCR
            itemIdInput.value = item.id;

            // Helper to safe set value
            const setValue = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.value = val || '';
            };

            setValue('nome_completo', dadosOcr.nome_completo || dadosOcr.nome);
            setValue('sexo', dadosOcr.sexo);
            setValue('data_nascimento', dadosOcr.data_nascimento);
            setValue('cpf', dadosOcr.cpf);
            setValue('escolaridade', dadosOcr.escolaridade);
            setValue('comunidade', dadosOcr.comunidade);
            setValue('ref_localizacao', dadosOcr.ref_localizacao);
            setValue('municipio', dadosOcr.municipio);
            setValue('estado_uf', dadosOcr.estado_uf);
            setValue('nis', dadosOcr.nis);

        } catch (error) {
            console.error(error);
            alert('Não foi possível carregar os dados para validação. Tente novamente.');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const jsonData = {};
        formData.forEach((value, key) => { jsonData[key] = value; });

        try {
            const response = await fetchWithAuth('/api/salvar-validado', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(jsonData)
            });

            if (response.ok) {
                alert('Beneficiário salvo com sucesso!');
                window.location.href = '/fila-validacao';
            } else {
                const errorData = await response.json();
                alert(`Ocorreu um erro ao salvar: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Erro de rede ao salvar:', error);
            alert('Ocorreu um erro de rede. Não foi possível salvar.');
        }
    });

    carregarDadosDoItem();
});
