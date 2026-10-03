let selectedFiles = [];
let uploadedFiles = {};

const fileInput = document.getElementById('files');
const uploadArea = document.getElementById('uploadArea');
const fileList = document.getElementById('fileList');
const uploadForm = document.getElementById('uploadForm');
const processBtn = document.getElementById('processBtn');
const baixarTodosBtn = document.getElementById('baixarTodos');
const limparBtn = document.getElementById('limpar');
const statusDiv = document.getElementById('status');

// Função para atualizar a cor do botão processar
function updateProcessButtonState() {
    if (selectedFiles.length > 0) {
        processBtn.classList.add('has-files');
    } else {
        processBtn.classList.remove('has-files');
    }
}

// Eventos de drag and drop
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files).filter(file =>
        file.name.toLowerCase().endsWith('.xlsx')
    );
    handleFiles(files);
});

// Seleção de arquivos
fileInput.addEventListener('change', (e) => {
    handleFiles(Array.from(e.target.files));
});

function handleFiles(files) {
    selectedFiles = [...selectedFiles, ...files];
    displayFileList();
    updateProcessButtonState();
}

function displayFileList() {
    if (selectedFiles.length === 0) {
        fileList.classList.remove('show');
        fileList.innerHTML = '';
        return;
    }

    fileList.classList.add('show');
    fileList.innerHTML = selectedFiles.map((file, index) => `
                <div class="file-item">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                    <button type="button" class="remove-file" onclick="removeFile(${index})">×</button>
                </div>
            `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFileList();
    updateProcessButtonState();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Upload e processamento
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (selectedFiles.length === 0) {
        alert('Por favor, selecione pelo menos um arquivo XLSX');
        return;
    }

    processBtn.disabled = true;
    processBtn.textContent = 'Enviando...';
    statusDiv.innerHTML = '';

    try {
        // Upload dos arquivos
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error('Erro ao enviar arquivos');
        }

        const uploadData = await uploadResponse.json();
        uploadData.files.forEach(file => {
            uploadedFiles[file.file_id] = file;
        });

        // Se limpou arquivos anteriores, atualiza a interface
        if (uploadData.cleared_previous > 0) {
            console.log(`${uploadData.cleared_previous} arquivo(s) anterior(es) limpo(s)`);
            // Limpa o status visual dos arquivos antigos
            await updateStatus();
        }

        // Processa os arquivos
        processBtn.textContent = 'Processando...';

        const processResponse = await fetch('/process', {
            method: 'POST'
        });

        if (!processResponse.ok) {
            throw new Error('Erro ao processar arquivos');
        }

        // Atualiza status
        await updateStatus();

        processBtn.textContent = 'Processar Arquivos';
        processBtn.disabled = false;

        // Limpa lista de arquivos selecionados
        selectedFiles = [];
        fileInput.value = '';
        displayFileList();
        updateProcessButtonState();

    } catch (error) {
        alert('Erro: ' + error.message);
        processBtn.textContent = 'Processar Arquivos';
        processBtn.disabled = false;
    }
});

async function updateStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        if (data.files.length === 0) {
            statusDiv.innerHTML = '';
            baixarTodosBtn.style.display = 'none';
            return;
        }

        // Verifica se há arquivos concluídos
        const completedFiles = data.files.filter(f => f.status === 'completed');
        if (completedFiles.length > 0) {
            baixarTodosBtn.style.display = 'inline-block';
        } else {
            baixarTodosBtn.style.display = 'none';
        }

        statusDiv.innerHTML = data.files.map(file => {
            let statusIcon = '⏳';
            let statusText = 'Aguardando...';
            let downloadBtn = '';
            let borderColor = '#FFA500';

            if (file.status === 'processing') {
                statusIcon = '⚙️';
                statusText = 'Processando...';
                borderColor = '#2196F3';
            } else if (file.status === 'completed') {
                statusIcon = '✅';
                statusText = 'Concluído';
                borderColor = '#4CAF50';
                downloadBtn = `<a href="/download/${file.file_id}" class="download-link" download>📥 Baixar TXT</a>`;
            } else if (file.status === 'error') {
                statusIcon = '❌';
                statusText = `Erro: ${file.error}`;
                borderColor = '#f44336';
            }

            return `
                        <div class="status-item" style="border-left-color: ${borderColor}">
                            <div class="status-info">
                                <span class="status-icon">${statusIcon}</span>
                                <span class="status-filename">${file.filename}</span>
                            </div>
                            <div class="status-state">
                                <span class="status-text">${statusText}</span>
                                ${downloadBtn}
                            </div>
                        </div>
                    `;
        }).join('');

        // Continua atualizando se ainda estiver processando
        if (data.processing) {
            setTimeout(updateStatus, 1000);
        }

    } catch (error) {
        console.error('Erro ao atualizar status:', error);
    }
}

// Limpar arquivos
limparBtn.addEventListener('click', async () => {
    if (!confirm('Deseja limpar todos os arquivos?')) {
        return;
    }

    try {
        await fetch('/clear', { method: 'POST' });

        selectedFiles = [];
        uploadedFiles = {};
        fileInput.value = '';
        displayFileList();
        statusDiv.innerHTML = '';
        baixarTodosBtn.style.display = 'none';
        updateProcessButtonState();

        alert('Arquivos limpos com sucesso!');
    } catch (error) {
        alert('Erro ao limpar arquivos: ' + error.message);
    }
});

// Baixar todos os arquivos
baixarTodosBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        const completedFiles = data.files.filter(f => f.status === 'completed');

        if (completedFiles.length === 0) {
            alert('Nenhum arquivo processado disponível para download');
            return;
        }

        baixarTodosBtn.disabled = true;
        baixarTodosBtn.textContent = `Baixando ${completedFiles.length} arquivo(s)...`;

        // Baixa cada arquivo com um pequeno delay
        for (let i = 0; i < completedFiles.length; i++) {
            const file = completedFiles[i];
            const link = document.createElement('a');
            link.href = `/download/${file.file_id}`;
            link.download = '';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Pequeno delay entre downloads para não sobrecarregar
            if (i < completedFiles.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 300));
            }
        }

        baixarTodosBtn.disabled = false;
        baixarTodosBtn.textContent = '📥 Baixar Todos';

    } catch (error) {
        alert('Erro ao baixar arquivos: ' + error.message);
        baixarTodosBtn.disabled = false;
        baixarTodosBtn.textContent = '📥 Baixar Todos';
    }
});

// Atualiza status ao carregar a página
window.addEventListener('load', updateStatus);