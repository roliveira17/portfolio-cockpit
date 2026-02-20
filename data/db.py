"""Conexão Supabase e funções CRUD para todas as tabelas."""

import logging

import streamlit as st

from supabase import Client, create_client

logger = logging.getLogger(__name__)


@st.cache_resource
def get_client() -> Client:
    """Retorna cliente Supabase singleton (cacheado por sessão)."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ============================================================
# Helpers genéricos
# ============================================================


def fetch_all(table: str, order_by: str = "created_at", ascending: bool = False) -> list[dict]:
    """Busca todos os registros de uma tabela, ordenados."""
    try:
        res = get_client().table(table).select("*").order(order_by, desc=not ascending).execute()
        return res.data
    except Exception:
        logger.warning(f"Supabase: falha ao buscar {table}")
        return []


def fetch_by_id(table: str, row_id: str) -> dict | None:
    """Busca um registro por ID."""
    res = get_client().table(table).select("*").eq("id", row_id).execute()
    return res.data[0] if res.data else None


def insert_row(table: str, data: dict) -> dict:
    """Insere um registro e retorna o dado inserido."""
    res = get_client().table(table).insert(data).execute()
    return res.data[0]


def insert_rows(table: str, data: list[dict]) -> list[dict]:
    """Insere múltiplos registros em batch."""
    res = get_client().table(table).insert(data).execute()
    return res.data


def update_row(table: str, row_id: str, data: dict) -> dict:
    """Atualiza um registro por ID."""
    res = get_client().table(table).update(data).eq("id", row_id).execute()
    return res.data[0]


def delete_row(table: str, row_id: str) -> None:
    """Deleta um registro por ID."""
    get_client().table(table).delete().eq("id", row_id).execute()


# ============================================================
# Positions
# ============================================================


def get_positions(active_only: bool = True) -> list[dict]:
    """Retorna posições, opcionalmente apenas ativas."""
    try:
        query = get_client().table("positions").select("*")
        if active_only:
            query = query.eq("is_active", True)
        return query.order("sector").execute().data
    except Exception:
        logger.warning("Supabase: falha ao buscar positions")
        return []


def get_position_by_ticker(ticker: str) -> dict | None:
    """Busca posição por ticker."""
    res = get_client().table("positions").select("*").eq("ticker", ticker).execute()
    return res.data[0] if res.data else None


# ============================================================
# Transactions
# ============================================================


def get_transactions(ticker: str | None = None) -> list[dict]:
    """Retorna transações, opcionalmente filtradas por ticker."""
    query = get_client().table("transactions").select("*")
    if ticker:
        query = query.eq("ticker", ticker)
    return query.order("date", desc=True).execute().data


# ============================================================
# Theses
# ============================================================


def get_theses() -> list[dict]:
    """Retorna todas as teses."""
    try:
        return get_client().table("theses").select("*").order("ticker").execute().data
    except Exception:
        logger.warning("Supabase: falha ao buscar theses")
        return []


def get_thesis_by_ticker(ticker: str) -> dict | None:
    """Busca tese por ticker."""
    res = get_client().table("theses").select("*").eq("ticker", ticker).execute()
    return res.data[0] if res.data else None


# ============================================================
# Catalysts
# ============================================================


def get_upcoming_catalysts(limit: int = 10) -> list[dict]:
    """Retorna próximos catalisadores não completados, ordenados por data."""
    try:
        return (
            get_client()
            .table("catalysts")
            .select("*")
            .eq("completed", False)
            .order("expected_date")
            .limit(limit)
            .execute()
            .data
        )
    except Exception:
        logger.warning("Supabase: falha ao buscar catalysts")
        return []


def get_catalysts_by_ticker(ticker: str) -> list[dict]:
    """Retorna catalisadores de um ticker, ordenados por data."""
    return (
        get_client().table("catalysts").select("*").eq("ticker", ticker).order("expected_date").execute().data
    )


def get_all_catalysts(include_completed: bool = False) -> list[dict]:
    """Retorna todos os catalisadores, opcionalmente incluindo completados."""
    query = get_client().table("catalysts").select("*")
    if not include_completed:
        query = query.eq("completed", False)
    return query.order("expected_date").execute().data


# ============================================================
# Macro Snapshots
# ============================================================


def get_latest_macro_snapshot() -> dict | None:
    """Retorna o snapshot macro mais recente."""
    res = get_client().table("macro_snapshots").select("*").order("date", desc=True).limit(1).execute()
    return res.data[0] if res.data else None


# ============================================================
# Deep Dives
# ============================================================


def get_deep_dives_by_ticker(ticker: str) -> list[dict]:
    """Retorna todos os deep dives de um ticker, versão mais recente primeiro."""
    return get_client().table("deep_dives").select("*").eq("ticker", ticker).order("version", desc=True).execute().data


def get_latest_deep_dive(ticker: str) -> dict | None:
    """Retorna o deep dive vigente (versão mais recente) de um ticker."""
    res = (
        get_client().table("deep_dives").select("*").eq("ticker", ticker).order("version", desc=True).limit(1).execute()
    )
    return res.data[0] if res.data else None


def get_all_deep_dives() -> list[dict]:
    """Retorna todos os deep dives, ordenados por data (mais recente primeiro)."""
    try:
        return get_client().table("deep_dives").select("*").order("date", desc=True).execute().data
    except Exception:
        logger.warning("Supabase: falha ao buscar deep_dives")
        return []


def get_next_deep_dive_version(ticker: str) -> int:
    """Retorna a próxima versão disponível para um ticker."""
    dives = get_deep_dives_by_ticker(ticker)
    if not dives:
        return 1
    return max(d["version"] for d in dives) + 1


# ============================================================
# Analysis Reports
# ============================================================


def get_analysis_reports(report_type: str | None = None) -> list[dict]:
    """Retorna relatórios, opcionalmente filtrados por tipo."""
    try:
        query = get_client().table("analysis_reports").select("*")
        if report_type:
            query = query.eq("report_type", report_type)
        return query.order("date", desc=True).execute().data
    except Exception:
        logger.warning("Supabase: falha ao buscar analysis_reports")
        return []


# ============================================================
# Portfolio Snapshots
# ============================================================


def get_portfolio_snapshots() -> list[dict]:
    """Retorna todos os snapshots do portfólio, ordenados por data."""
    try:
        return get_client().table("portfolio_snapshots").select("*").order("date").execute().data
    except Exception:
        logger.warning("Supabase: falha ao buscar portfolio_snapshots")
        return []


def get_latest_portfolio_snapshot() -> dict | None:
    """Retorna o snapshot mais recente do portfólio."""
    try:
        res = get_client().table("portfolio_snapshots").select("*").order("date", desc=True).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception:
        logger.warning("Supabase: falha ao buscar último portfolio_snapshot")
        return None


def save_portfolio_snapshot(data: dict) -> dict:
    """Salva snapshot do portfólio. Chamado no page load do Overview (1x/dia)."""
    return insert_row("portfolio_snapshots", data)
