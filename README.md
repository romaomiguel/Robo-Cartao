# Robô de Cartões — Processador de relatórios de adquirentes

Aplicação web que transforma **relatórios de vendas de cartão** (planilhas `.xlsx` de adquirentes como Cielo, GetNet, Rede, Stone, Safra, Sicredi, Sipag, PagSeguro, Alelo, Sodexo e outros) em um **arquivo `.txt` de lançamentos contábeis**, pronto para importar no sistema contábil.

> Versão pública de um projeto real de uso interno. Nomes de clientes foram substituídos por `cliente a`, `cliente b`... e os códigos de conta são exemplos.

## O problema

Cada adquirente exporta a planilha em um layout diferente (nome das colunas, onde começa o cabeçalho, como separar débito/crédito). Lançar à mão o **valor bruto** e a **taxa** de cada venda leva horas por cliente. O robô faz isso em segundos.

## Como funciona

1. O usuário envia um ou mais `.xlsx` na tela (upload com acompanhamento de progresso).
2. O sistema identifica o **perfil do cartão** pelo nome do arquivo (ex.: `cielo credito`, `get net debito`, `stone credito`).
3. Cada perfil define quais colunas ler (`palavra_data`, `palavra_valor`, `palavra_taxa`), qual ocorrência do cabeçalho usar e **duas linhas de lançamento** por venda: uma para o valor bruto e outra para a taxa — `conta débito;conta crédito;histórico`.
4. Perfis avançados suportam: **identificar débito/crédito por coluna** (ex.: `Produto`), ignorar valores negativos, complementos de histórico personalizados e contas diferentes por modalidade.
5. O resultado é entregue como `.txt` para download.

Os perfis são editáveis em um **painel `/admin`** protegido por senha (criar, editar e excluir), sem mexer em código. Ficam no PostgreSQL (com carga inicial a partir de `DEFAULT_PARAMETROS` em `config.py`).

## Stack

Python 3 · Flask · openpyxl / pandas / xlrd · PostgreSQL (`psycopg2`) · SQLite para sessões de processamento · Gunicorn · Docker · Kubernetes

## Como rodar

```bash
pip install -r requirements.txt
export ADMIN_PASSWORD="troque-esta-senha"
export SECRET_KEY="troque-esta-chave"
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/robo_cartao"   # opcional; sem ele usa arquivo JSON local
python app.py          # http://localhost:2929
```

Com Docker: `docker build -t robo-cartao . && docker run -p 2929:2929 robo-cartao`.

### Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave de sessão do Flask |
| `ADMIN_PASSWORD` | Senha do painel `/admin` |
| `DATABASE_URL` | PostgreSQL para guardar os perfis (opcional) |
| `FLASK_DEBUG` (padrão `False`), `FLASK_HOST`, `FLASK_PORT` | Servidor |
| `UPLOAD_FOLDER`, `OUTPUT_FOLDER` | Pastas de trabalho |
| `MAX_FILE_SIZE` | Limite de upload (padrão 16 MB) |
| `SESSION_TIMEOUT` | Expiração da sessão em segundos |

## Rotas

| Rota | Função |
|---|---|
| `POST /upload` | Recebe planilhas |
| `POST /process` | Inicia o processamento (em thread) |
| `GET /status` | Progresso por arquivo |
| `GET /download/<id>` | Baixa o `.txt` |
| `GET /health` | Saúde (probe do Kubernetes) |
| `/admin` | Gestão dos perfis de cartão |

## Estrutura

```
app.py        rotas, leitura das planilhas e geração do TXT
config.py     configuração e perfis padrão de cartão
db.py         persistência dos perfis (PostgreSQL)
templates/    telas (upload e admin)
static/       CSS e JS
k8s-deployment.example.yaml   exemplo de manifest
```

## Deploy

Exemplo de manifest em [`k8s-deployment.example.yaml`](k8s-deployment.example.yaml). O workflow `.github/workflows/build-push.yml` constrói a imagem, publica no GHCR e atualiza a tag no `k8s-manifests`; ajuste `seu-usuario` para a sua conta.
