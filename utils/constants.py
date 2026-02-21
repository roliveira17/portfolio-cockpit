"""Constantes do projeto: tickers, setores, benchmarks, cores, sensibilidades."""

# ============================================================
# Tickers por mercado
# ============================================================

TICKERS_BR = ["INBR32", "ENGI4", "EQTL3", "ALOS3", "SUZB3", "KLBN4", "BRAV3", "PLPL3", "RAPT4", "GMAT3"]
TICKERS_US = ["TSM", "NVDA", "ASML", "MELI", "GOOGL", "SNPS", "MU"]
TICKERS_OTHER = ["FIDC_MICROCREDITO", "ELET_FMP", "CAIXA"]
TICKERS_ALL = TICKERS_BR + TICKERS_US + TICKERS_OTHER

# ============================================================
# Setores — PRD seção 9.2
# ============================================================

SECTORS = {
    "financeiro": {"label": "Financeiro & Crédito", "color": "#1f77b4"},
    "utilities": {"label": "Utilities & Concessões", "color": "#ff7f0e"},
    "consumo_varejo": {"label": "Consumo, Varejo & Imobiliário", "color": "#2ca02c"},
    "energia_materiais": {"label": "Energia & Materiais Básicos", "color": "#d62728"},
    "tech_semis": {"label": "Tecnologia & Semicondutores", "color": "#9467bd"},
    "fundos": {"label": "Fundos", "color": "#8c564b"},
    "caixa": {"label": "Caixa", "color": "#7f7f7f"},
}

# ============================================================
# Benchmarks — PRD seção 9.1
# ============================================================

BENCHMARKS = {
    "primary": {"name": "IBOV", "ticker": "^BVSP"},
    "hurdle": {"name": "CDI", "series_bcb": 12},
}

# ============================================================
# Tickers yfinance para dados macro — PRD seção 5.5
# ============================================================

MACRO_TICKERS = {
    "sp500": "^GSPC",
    "vix": "^VIX",
    "dxy": "DX-Y.NYB",
    "brent": "BZ=F",
    "treasury_10y": "^TNX",
    "ibov": "^BVSP",
}

# Séries BCB — PRD seção 5.4
BCB_SERIES = {
    "selic": 432,
    "ipca_mensal": 433,
    "ipca_12m": 13522,
    "cdi": 12,
    "ptax": 1,
}

# ============================================================
# Mapeamento ticker → setor (para consultas rápidas)
# ============================================================

TICKER_SECTOR = {
    "INBR32": "financeiro",
    "ENGI4": "utilities",
    "EQTL3": "utilities",
    "ALOS3": "consumo_varejo",
    "SUZB3": "energia_materiais",
    "KLBN4": "energia_materiais",
    "BRAV3": "energia_materiais",
    "PLPL3": "consumo_varejo",
    "RAPT4": "consumo_varejo",
    "GMAT3": "consumo_varejo",
    "TSM": "tech_semis",
    "NVDA": "tech_semis",
    "ASML": "tech_semis",
    "MELI": "tech_semis",
    "GOOGL": "tech_semis",
    "SNPS": "tech_semis",
    "MU": "tech_semis",
    "FIDC_MICROCREDITO": "fundos",
    "ELET_FMP": "fundos",
    "CAIXA": "caixa",
}

# ============================================================
# Sensibilidades a fatores — PRD seção 9.3
# Usadas em stress tests (Simulator)
# ============================================================

FACTOR_SENSITIVITIES = {
    "selic_1pp": {
        "INBR32": -0.05,
        "ENGI4": -0.08,
        "EQTL3": -0.07,
        "ALOS3": -0.06,
        "PLPL3": -0.04,
        "SUZB3": -0.02,
        "KLBN4": -0.02,
        "BRAV3": 0.00,
        "RAPT4": -0.03,
        "GMAT3": -0.03,
    },
    "usdbrl_10pct": {
        "SUZB3": +0.08,
        "KLBN4": +0.06,
        "BRAV3": +0.05,
        "TSM": -0.10,
        "NVDA": -0.10,
        "ASML": -0.10,
        "MELI": -0.10,
        "GOOGL": -0.10,
        "SNPS": -0.10,
        "MU": -0.10,
    },
    "brent_10pct": {
        "BRAV3": +0.12,
    },
    "ibov_10pct": {
        "INBR32": 1.2,
        "ENGI4": 0.6,
        "EQTL3": 0.7,
        "ALOS3": 0.8,
        "SUZB3": 0.9,
        "KLBN4": 0.7,
        "BRAV3": 1.3,
        "PLPL3": 1.1,
        "RAPT4": 1.0,
        "GMAT3": 0.8,
    },
}

# ============================================================
# Cache TTLs (segundos) — PRD seção 8
# ============================================================

CACHE_TTL_QUOTES = 15 * 60  # 15 minutos
CACHE_TTL_MACRO = 60 * 60  # 1 hora
CACHE_TTL_DB = 5 * 60  # 5 minutos

# ============================================================
# Labels para Thesis Board — PRD seção 6.4
# ============================================================

THESIS_STATUS = {
    "GREEN": {"emoji": "🟢", "label": "Ativa"},
    "YELLOW": {"emoji": "🟡", "label": "Revisão"},
    "RED": {"emoji": "🔴", "label": "Crítica"},
}

CONVICTION_LABELS = {"HIGH": "Alta", "MEDIUM": "Média", "LOW": "Baixa"}

MOAT_LABELS = {"STRONG": "Forte", "MODERATE": "Moderado", "WEAK": "Fraco", "NONE": "Sem Moat"}

MOAT_TREND_LABELS = {"WIDENING": "Ampliando", "STABLE": "Estável", "NARROWING": "Estreitando"}

CATALYST_CATEGORIES = {
    "EARNINGS": "Resultados",
    "REGULATORY": "Regulatório",
    "MACRO": "Macro",
    "CORPORATE": "Corporativo",
    "OTHER": "Outro",
}

IMPACT_LABELS = {"HIGH": "Alto", "MEDIUM": "Médio", "LOW": "Baixo"}

# ============================================================
# Labels para Knowledge Base — PRD seção 6.6
# ============================================================

REPORT_TYPES = {
    "MACRO": "Macro",
    "SECTOR": "Setorial",
    "THEMATIC": "Temático",
    "PORTFOLIO_REVIEW": "Revisão de Portfólio",
}

# ============================================================
# OpenRouter Models — Chat page (Sprint 5)
# ============================================================

OPENROUTER_MODELS = {
    "Claude Sonnet 4.6 (~$2.25/sessão)": {"id": "anthropic/claude-sonnet-4-20250514", "supports_vision": True},
    "Claude Haiku 4.5 (~$0.75)": {"id": "anthropic/claude-haiku-4-20250514", "supports_vision": True},
    "Claude Opus 4.6 (~$3.75)": {"id": "anthropic/claude-opus-4-20250514", "supports_vision": True},
    "Gemini 2.5 Flash (~$0.26)": {"id": "google/gemini-2.5-flash-preview", "supports_vision": True},
    "Gemini 2.5 Pro (~$1.06)": {"id": "google/gemini-2.5-pro-preview", "supports_vision": True},
    "GPT-4o (~$2.86)": {"id": "openai/gpt-4o", "supports_vision": True},
    "GPT-4o-mini (~$0.17)": {"id": "openai/gpt-4o-mini", "supports_vision": True},
    "DeepSeek R1 (~$0.92)": {"id": "deepseek/deepseek-r1", "supports_vision": False},
    "Kimi K2": {"id": "moonshotai/kimi-k2", "supports_vision": False},
}
