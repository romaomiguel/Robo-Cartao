FROM python:3.11-slim

WORKDIR /app

# Instalar dependências necessárias para compilar algumas bibliotecas Python se necessário
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria os diretórios necessários
RUN mkdir -p uploads outputs

# Expõe a porta original
EXPOSE 2929

# 1 worker + threads (não --preload com múltiplos workers): cada worker extra
# com --preload duplica o consumo de memória e quebra o cache em memória de
# PARAMETROS entre processos — mesmo padrão de correção já aplicado no Robô
# ICMS (ver manual operacional do cluster, seção 14).
CMD ["gunicorn", "--bind", "0.0.0.0:2929", "--workers", "1", "--worker-class", "gthread", "--threads", "4", "--timeout", "120", "app:app"]
