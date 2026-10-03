"""
Acesso ao Postgres compartilhado do cluster (CloudNativePG) para persistir
as configurações de cartão (PARAMETROS) usadas pelo painel /admin.

Segue o padrão do manual operacional do cluster: módulo próprio com
CREATE TABLE IF NOT EXISTS na inicialização — a tabela nasce sozinha,
sem precisar rodar migration manual.
"""

import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get('DATABASE_URL')


@contextmanager
def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Cria a tabela de parâmetros de cartão, se ainda não existir."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS parametros_cartao (
                    chave TEXT PRIMARY KEY,
                    config JSONB NOT NULL,
                    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)


def seed_se_vazio(parametros_padrao):
    """Na primeira execução (tabela vazia), popula com os parâmetros de fábrica
    definidos em config.DEFAULT_PARAMETROS — preserva o comportamento atual
    dos cartões já configurados quando o banco entra em uso pela primeira vez."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM parametros_cartao")
            (total,) = cur.fetchone()
            if total > 0:
                return
            for chave, config in parametros_padrao.items():
                cur.execute(
                    "INSERT INTO parametros_cartao (chave, config) VALUES (%s, %s) "
                    "ON CONFLICT (chave) DO NOTHING",
                    (chave, psycopg2.extras.Json(config))
                )


def carregar_todos():
    """Retorna {chave: config} com todas as configurações cadastradas."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT chave, config FROM parametros_cartao ORDER BY chave")
            return {chave: config for chave, config in cur.fetchall()}


def upsert(chave, config):
    """Cria ou atualiza uma configuração de cartão."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO parametros_cartao (chave, config, atualizado_em) VALUES (%s, %s, now()) "
                "ON CONFLICT (chave) DO UPDATE SET config = EXCLUDED.config, atualizado_em = now()",
                (chave, psycopg2.extras.Json(config))
            )


def excluir(chave):
    """Remove uma configuração de cartão."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM parametros_cartao WHERE chave = %s", (chave,))
