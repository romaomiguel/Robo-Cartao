"""
Arquivo de configuração do Processador de Cartões
Centralize todas as configurações aqui para facilitar manutenção
"""

import os
import json
import time
import threading

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 2929))

    # Pastas
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', 'outputs')

    # Extensões permitidas
    ALLOWED_EXTENSIONS = {'xlsx'}

    # Tamanho máximo de arquivo (em bytes) - 16MB padrão
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))

    # Tempo de expiração da sessão (em segundos) - 24 horas padrão
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 86400))

    # Senha do painel /admin de configuração de PARAMETROS.
    # Troque via variável de ambiente em produção — nunca deixe o padrão.
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'mude-esta-senha')


# =========================
# PARÂMETROS POR TIPO DE CARTÃO
# =========================

# Linha 1 -> # Conta p/ Vlr Bruto {Conta 1, Conta 2, Historico}
# Linha 2 -> # Conta p/ Taxa {Conta 1, Conta 2, Historico}

DEFAULT_PARAMETROS = {
    "cielo credito": { # Nome do arquivo
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Taxa/tarifa",
        "ocorrencia": 2,
        "linha1": "4920;4918;359",
        "linha2": "1228;4920;363",
    },
    "cielo debito": { # Nome do arquivo
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Taxa/tarifa",
        "ocorrencia": 2,
        "linha1": "4922;4918;360",
        "linha2": "1228;4922;364",
    },
    "cliente a cielo": { # Nome do arquivo
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Taxa/tarifa",
        "ocorrencia": 2,
        "linha1": "4920;4918;360",
        "linha2": "1228;4920;364",
    },
    "get net credito": { # Nome do arquivo
        "palavra_data": "DATA/HORA DA VENDA",
        "palavra_valor": "VALOR BRUTO",
        "palavra_taxa": "VALOR TAXA",
        "ocorrencia": 1,
        "linha1": "1191;4918;448",
        "linha2": "1228;1191;450",
    },
    "get net debito": { # Nome do arquivo
        "palavra_data": "DATA/HORA DA VENDA",
        "palavra_valor": "VALOR BRUTO",
        "palavra_taxa": "VALOR TAXA",
        "ocorrencia": 1,
        "linha1": "1192;4918;447",
        "linha2": "1228;1192;449",
    },
    "get net antecipacao": { # Nome do arquivo
        "palavra_data": "DATA DA CONTRATAÇÃO",
        "palavra_valor": "VALOR ATUAL",
        "palavra_taxa": "TAXA DESCONTO",
        "ocorrencia": 1,
        "linha1": "5015;1191;22",
        "linha2": "4701;5015;370",
    },
    "redecard credito": { # Nome do arquivo
        "palavra_data": "data da venda",
        "palavra_valor": "valor da venda atualizado",
        "palavra_taxa": "valor MDR",
        "ocorrencia": 1,
        "linha1": "4921;4918;361",
        "linha2": "1228;4921;365",
    },
    "redecard debito": { # Nome do arquivo
        "palavra_data": "data da venda",
        "palavra_valor": "valor da venda atualizado",
        "palavra_taxa": "valor MDR",
        "ocorrencia": 1,
        "linha1": "4923;4918;362",
        "linha2": "1228;4923;366",
    },
    "stone debito": { # Nome do arquivo
        "palavra_data": "DATA DA VENDA",
        "palavra_valor": "VALOR BRUTO",
        "palavra_taxa": "DESCONTO DE MDR",
        "ocorrencia": 1,
        "linha1": "5032;1270;372",
        "linha2": "1226;1270;456",
    },    
    "stone credito": { # Nome do arquivo
        "palavra_data": "DATA DA VENDA",
        "palavra_valor": "VALOR BRUTO",
        "palavra_taxa": "DESCONTO DE MDR",
        "ocorrencia": 1,
        "linha1": "5032;1271;372",
        "linha2": "1226;1271;456",
    },
    "cliente b get net": { # Nome do arquivo
        "palavra_data": "Data/Hora \nda Venda",
        "palavra_valor": "Valor Bruto",
        "palavra_taxa": "Valor da Taxa \ne/ou Tarifa",
        "ocorrencia": 1,
        "linha1": "1191;142;448",
        "linha2": "1228;1191;450",
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo

    },
    "truckpag credito": { # Nome do arquivo
        "palavra_data": "Data Transacao",
        "palavra_valor": "Valor Total",
        "palavra_taxa": "Taxa",
        "ocorrencia": 1,
        "linha1": "5020;4918;354",
        "linha2": "1228;5020;355",
        "complemento": "TRUCKPAG",
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo


    },
    "ticket credito": { # Nome do arquivo
        "palavra_data": "Data / Hora",
        "palavra_valor": "Valor Bruto",
        "palavra_taxa": "Valor Descontado",
        "ocorrencia": 1,
        "linha1": "808;4918;405",
        "linha2": "1228;808;407", 
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo

    },
    "sodexo credito": { # Nome do arquivo
        "palavra_data": "Data da transação",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Taxa",
        "ocorrencia": 1,
        "linha1": "819;4918;403", 
        "linha2": "1228;819;404",  
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo

    },
    "shellbox credito": { # Nome do arquivo
        "palavra_data": "Data da Transação",
        "palavra_valor": "Valor do Pagamento",
        "palavra_taxa": "Taxa",
        "ocorrencia": 1,
        "linha1": "5013;4918;354", 
        "linha2": "1228;5013;355",  
        "complemento": "SHELL",
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo

    },
    "safra credito": { # Nome do arquivo
        "palavra_data": "Data da Venda",
        "palavra_valor": "Valor Bruto da Venda",
        "palavra_taxa": "Taxa",
        "ocorrencia": 1,
        "linha1": "1265;4918;493", 
        "linha2": "1228;1265;355",  
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo
    },
    "safra debito": { # Nome do arquivo
        "palavra_data": "Data da Venda",
        "palavra_valor": "Valor Bruto da Venda",
        "palavra_taxa": "Taxa",
        "ocorrencia": 1,
        "linha1": "1266;4918;492", 
        "linha2": "1228;1266;355",  
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo
    },
    "pagseguro": { # Nome do arquivo
        "palavra_data": "Data da Transação",
        "palavra_valor": "Valor Bruto",
        "palavra_taxa": "Valor Taxa",
        "ocorrencia": 1,
        "linha1": "1238;4918;354", 
        "linha2": "1228;1238;355",  
        "complemento": "PAG SEGURO",
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo
    },
    "alelo credito": { # Nome do arquivo
        "palavra_data": "Data da Venda",
        "palavra_valor": "Valor Bruto",
        "palavra_taxa": "Taxa",
        "ocorrencia": 1,
        "linha1": "4920;4918;359", 
        "linha2": "1228;4920;363",  
        "ignorar_valores_negativos": True,  # Ignora linhas com valor bruto negativo
    },
    "cliente c sicredi debito e credito": {
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Valor da taxa",
        "ocorrencia": 1,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Produto",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito"],
                "linha1": "5017;142;486",
                "linha2": "1228;5017;487",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito à vista", "Parcelado Lojista"],
                "linha1": "5016;142;485",
                "linha2": "1228;5016;488",
            }
        }
    },
    "cliente d sicredi debito e credito": {
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Valor da taxa",
        "ocorrencia": 1,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Produto",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito"],
                "linha1": "428;4918;483",
                "linha2": "1228;428;481",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito à vista", "Parcelado Lojista"],
                "linha1": "429;4918;482",
                "linha2": "1228;429;480",
            }
        }
    },
    "cliente e sicredi debito e credito": {
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto da transação",
        "palavra_taxa": "Valor da taxa (MDR)",
        "ocorrencia": 1,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Produto",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito"],
                "linha1": "428;4918;483",
                "linha2": "1228;428;481",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito a Vista"],
                "linha1": "429;4918;482",
                "linha2": "1228;429;480",
            }
        }
    },
    "cliente f cielo": {
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Taxa/tarifa",
        "ocorrencia": 2,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Forma de pagamento",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito à vista", "Débito pré-pago"],
                "linha1": "4922;4918;360",
                "linha2": "1228;4922;364",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito à vista", "Crédito parcelado loja"],
                "linha1": "4920;4918;359",
                "linha2": "1228;4920;363",
            }
        }
    },
    "cliente g sicredi": {
        "palavra_data": "Data",
        "palavra_valor": "Valor total",
        "palavra_taxa": "Taxa",
        "ocorrencia": 2,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Tipo de venda",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["DEBIT"],
                "linha1": "5009;4918;354",
                "linha2": "1228;5009;355",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["CREDIT"],
                "linha1": "5010;4918;354",
                "linha2": "1228;5010;355",
            }
        }
    },
    "cliente h stone": {
        "palavra_data": "DATA DA VENDA",
        "palavra_valor": "VALOR BRUTO",
        "palavra_taxa": "DESCONTO DE MDR",
        "ocorrencia": 2,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "PRODUTO",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito", "Débito Pré-pago"],
                "linha1": "1270;4918;455",
                "linha2": "1228;1270;456",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito", "Crédito Pré-pago"],
                "linha1": "1271;4918;455",
                "linha2": "1228;1271;456",
            }
        }
    },
    "unicred debito e credito": {
        "palavra_data": "Data Trans.",
        "palavra_valor": "Valor Bruto",
        "palavra_taxa": "Desconto",
        "ocorrencia": 1,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Tipo",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["DÉBITO"],
                "linha1": "5011;4918;350",
                "linha2": "1227;5011;350",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["CRÉDITO"],
                "linha1": "5012;4918;350",
                "linha2": "1227;5012;350",
            }
        },
        "complemento_debito": "VENDA CARTÃO UNICRED DEBITO",
        "complemento_debito_desconto": "COMISSÃO CARTÃO UNICRED DEBITO",
        "complemento_credito": "VENDA CARTÃO UNICRED CREDITO",
        "complemento_credito_desconto": "COMISSÃO CARTÃO UNICRED CREDITO"
    },
    "cliente i debito e credito": {
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor Bruto",
        "palavra_taxa": "Valor da taxa (MDR)",
        "ocorrencia": 2,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Modalidade",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito", "Débito Internacional"],
                "linha1": "5107;4918;354",
                "linha2": "1227;5107;355",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito", "Crédito à vista"],
                "linha1": "5106;4918;354",
                "linha2": "1227;5106;355",
            }
        },
        "complemento_debito": "DEBITO CLIENTE I",
        "complemento_debito_desconto": "CLIENTE I",
        "complemento_credito": "CREDITO CLIENTE I",
        "complemento_credito_desconto": "CLIENTE I"
    },
    "sipag sicoob": {
        "palavra_data": "Data do pagamento",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Valor líquido",
        "ocorrencia": 2,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Produto",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito", "Débito à vista"],
                "linha1": "1236;142;354",
                "linha2": "1228;1236;355",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito", "Crédito à vista"],
                "linha1": "1235;142;354",
                "linha2": "1228;1235;355",
            }
        },
        "complemento_debito": "SIPAG DEBITO",
        "complemento_debito_desconto": "SIPAG DEBITO",
        "complemento_credito": "SIPAG CREDITO",
        "complemento_credito_desconto": "SIPAG CREDITO"
    },
    "arquivo teste": {
        "palavra_data": "Data da venda",
        "palavra_valor": "Valor bruto",
        "palavra_taxa": "Valor da taxa",
        "ocorrencia": 2,
        # Configuração para identificar débito/crédito por coluna
        "identificar_por_coluna": {
            "nome_coluna": "Produto",  # Nome da coluna que tem "Debito" ou "Credito"
            "debito": {
                # Valores possíveis que indicam débito (case-insensitive)
                "valores": ["Débito", "Débito à vista"],
                "linha1": "428;4918;483",
                "linha2": "1228;428;481",
            },
            "credito": {
                # Valores possíveis que indicam crédito (case-insensitive)
                "valores": ["Crédito", "Crédito à vista", "Parcelado Lojista"],
                "linha1": "429;4918;482",
                "linha2": "1228;429;480",
            }
        }
    },
}

# =========================
# PERSISTÊNCIA DOS PARÂMETROS (editáveis pelo painel /admin)
# =========================
# Fonte de verdade: Postgres compartilhado do cluster (tabela parametros_cartao,
# ver db.py), sempre que a variável de ambiente DATABASE_URL estiver definida
# — é o caso em produção (Secret robo-cartao-db-creds). Sem DATABASE_URL (ex:
# rodando localmente sem um Postgres à mão) cai para um arquivo JSON em disco,
# só para permitir testar o painel sem precisar subir um banco.
# DEFAULT_PARAMETROS acima continua servindo como carga inicial: na primeira
# vez que a tabela é criada (ou o JSON não existe ainda), os cartões já
# configurados hoje são semeados automaticamente.
USANDO_POSTGRES = bool(os.environ.get('DATABASE_URL'))

PARAMETROS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parametros_config.json')

_parametros_lock = threading.Lock()
_parametros_cache = {"data": None, "mtime": None, "ts": 0.0}
_CACHE_TTL_SEGUNDOS = 5  # só relevante no fallback via Postgres; o fallback via arquivo usa mtime


def _carregar_arquivo_json():
    if os.path.exists(PARAMETROS_FILE):
        try:
            with open(PARAMETROS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    _salvar_arquivo_json(DEFAULT_PARAMETROS)
    return json.loads(json.dumps(DEFAULT_PARAMETROS))


def _salvar_arquivo_json(data):
    with open(PARAMETROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if USANDO_POSTGRES:
    import db as _db
    _db.init_db()
    _db.seed_se_vazio(DEFAULT_PARAMETROS)


def get_parametros():
    """Retorna todas as configurações de cartão cadastradas.

    Com Postgres: cache em memória de alguns segundos (evita bater no banco a
    cada arquivo processado num lote) — como o Gunicorn roda 1 worker com
    threads (ver Dockerfile), a invalidação feita em upsert_parametro/
    delete_parametro já é vista por todas as requisições na hora.
    Sem Postgres: relê o JSON do disco sempre que o arquivo muda (por mtime).
    """
    with _parametros_lock:
        if USANDO_POSTGRES:
            agora = time.monotonic()
            if _parametros_cache["data"] is None or (agora - _parametros_cache["ts"]) > _CACHE_TTL_SEGUNDOS:
                _parametros_cache["data"] = _db.carregar_todos()
                _parametros_cache["ts"] = agora
        else:
            try:
                mtime = os.path.getmtime(PARAMETROS_FILE)
            except OSError:
                mtime = None
            if _parametros_cache["data"] is None or mtime != _parametros_cache["mtime"]:
                _parametros_cache["data"] = _carregar_arquivo_json()
                _parametros_cache["mtime"] = mtime
        return _parametros_cache["data"]


def _invalidar_cache():
    with _parametros_lock:
        _parametros_cache["data"] = None


def upsert_parametro(chave, dado):
    """Cria ou atualiza uma única configuração de cartão."""
    if USANDO_POSTGRES:
        _db.upsert(chave, dado)
    else:
        atual = dict(get_parametros())
        atual[chave] = dado
        _salvar_arquivo_json(atual)
    _invalidar_cache()


def delete_parametro(chave):
    """Remove uma configuração de cartão."""
    if USANDO_POSTGRES:
        _db.excluir(chave)
    else:
        atual = dict(get_parametros())
        atual.pop(chave, None)
        _salvar_arquivo_json(atual)
    _invalidar_cache()


# =========================
# MENSAGENS PERSONALIZADAS
# =========================
MESSAGES = {
    'upload_success': '{count} arquivo(s) enviado(s) com sucesso',
    'upload_error': 'Nenhum arquivo enviado',
    'processing_complete': 'Processamento concluído',
    'processing_error': 'Erro ao processar arquivos',
    'file_not_found': 'Arquivo não encontrado',
    'file_not_processed': 'Arquivo ainda não foi processado',
    'clear_success': 'Arquivos limpos com sucesso',
    'type_not_identified': 'Tipo de cartão não identificado no nome do arquivo. O nome deve conter: "cielo credito", "cielo debito", "get net credito", "get net debito", "redecard credito", "redecard debito" ou "stone"',
    'column_not_found': '✗ Coluna {column} não encontrada (procurava por: "{word}")',
    'type_column_not_found': '⚠️ Coluna "{column}" não encontrada na planilha. Esta coluna é necessária para identificar se cada transação é débito ou crédito. Verifique se o nome da coluna está correto no arquivo config.py',
}
