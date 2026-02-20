"""Popular banco de dados com dados iniciais do portfólio (PRD seção 4)."""

import re
import tomllib
from pathlib import Path

from supabase import create_client

SECRETS_PATH = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"

# ============================================================
# Dados das posições — PRD seção 4.1, 4.2, 4.3
# ============================================================

POSITIONS_BR = [
    {
        "ticker": "INBR32",
        "company_name": "Inter & Co Inc.",
        "market": "BR",
        "currency": "BRL",
        "sector": "financeiro",
        "analyst": "Analista Financeiro & Crédito",
        "quantity": 1905,
        "avg_price": 32.67,
        "total_invested": 62244.54,
        "dividends_received": 503.37,
    },
    {
        "ticker": "ENGI4",
        "company_name": "Energisa",
        "market": "BR",
        "currency": "BRL",
        "sector": "utilities",
        "analyst": "Analista de Utilities & Concessões",
        "quantity": 4390,
        "avg_price": 8.04,
        "total_invested": 35280.47,
        "dividends_received": 5354.85,
    },
    {
        "ticker": "EQTL3",
        "company_name": "Equatorial",
        "market": "BR",
        "currency": "BRL",
        "sector": "utilities",
        "analyst": "Analista de Utilities & Concessões",
        "quantity": 642,
        "avg_price": 31.23,
        "total_invested": 20052.57,
        "dividends_received": 1529.79,
    },
    {
        "ticker": "ALOS3",
        "company_name": "Aliansce Sonae",
        "market": "BR",
        "currency": "BRL",
        "sector": "consumo_varejo",
        "analyst": "Analista de Consumo, Varejo & Imobiliário",
        "quantity": 800,
        "avg_price": 18.87,
        "total_invested": 15092.91,
        "dividends_received": 1439.85,
    },
    {
        "ticker": "SUZB3",
        "company_name": "Suzano",
        "market": "BR",
        "currency": "BRL",
        "sector": "energia_materiais",
        "analyst": "Analista de Energia & Materiais",
        "quantity": 400,
        "avg_price": 51.04,
        "total_invested": 20414.94,
        "dividends_received": 699.11,
    },
    {
        "ticker": "KLBN4",
        "company_name": "Klabin",
        "market": "BR",
        "currency": "BRL",
        "sector": "energia_materiais",
        "analyst": "Analista de Energia & Materiais",
        "quantity": 5383,
        "avg_price": 3.73,
        "total_invested": 20097.16,
        "dividends_received": 1937.48,
    },
    {
        "ticker": "BRAV3",
        "company_name": "Brava Energia",
        "market": "BR",
        "currency": "BRL",
        "sector": "energia_materiais",
        "analyst": "Analista de Energia & Materiais",
        "quantity": 1000,
        "avg_price": 15.86,
        "total_invested": 15858.00,
        "dividends_received": 0,
    },
    {
        "ticker": "PLPL3",
        "company_name": "Plano & Plano",
        "market": "BR",
        "currency": "BRL",
        "sector": "consumo_varejo",
        "analyst": "Analista de Consumo, Varejo & Imobiliário",
        "quantity": 1100,
        "avg_price": 13.72,
        "total_invested": 15088.68,
        "dividends_received": 0,
    },
    {
        "ticker": "RAPT4",
        "company_name": "Empresas Randon",
        "market": "BR",
        "currency": "BRL",
        "sector": "consumo_varejo",
        "analyst": "Analista de Consumo, Varejo & Imobiliário",
        "quantity": 2500,
        "avg_price": 6.02,
        "total_invested": 15057.67,
        "dividends_received": 0,
    },
    {
        "ticker": "GMAT3",
        "company_name": "Grupo Mateus",
        "market": "BR",
        "currency": "BRL",
        "sector": "consumo_varejo",
        "analyst": "Analista de Consumo, Varejo & Imobiliário",
        "quantity": 2600,
        "avg_price": 4.91,
        "total_invested": 12773.07,
        "dividends_received": 0,
    },
]

POSITIONS_US = [
    {
        "ticker": "TSM",
        "company_name": "Taiwan Semiconductor",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 10.51,
        "avg_price": 333.01,
        "total_invested": 3499.26,
        "dividends_received": 0,
    },
    {
        "ticker": "NVDA",
        "company_name": "Nvidia",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 15.69,
        "avg_price": 191.23,
        "total_invested": 2999.99,
        "dividends_received": 0,
    },
    {
        "ticker": "ASML",
        "company_name": "ASML Holding",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 1.51,
        "avg_price": 1455.97,
        "total_invested": 2199.98,
        "dividends_received": 0,
    },
    {
        "ticker": "MELI",
        "company_name": "MercadoLibre",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 0.64,
        "avg_price": 2193.50,
        "total_invested": 1403.84,
        "dividends_received": 0,
    },
    {
        "ticker": "GOOGL",
        "company_name": "Alphabet",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 3.85,
        "avg_price": 259.84,
        "total_invested": 1000.65,
        "dividends_received": 0,
    },
    {
        "ticker": "SNPS",
        "company_name": "Synopsys",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 2.47,
        "avg_price": 485.24,
        "total_invested": 1199.99,
        "dividends_received": 0,
    },
    {
        "ticker": "MU",
        "company_name": "Micron Technology",
        "market": "US",
        "currency": "USD",
        "sector": "tech_semis",
        "analyst": "Analista de Tecnologia & Semicondutores",
        "quantity": 2.21,
        "avg_price": 405.17,
        "total_invested": 896.24,
        "dividends_received": 0,
    },
]

POSITIONS_OTHER = [
    {
        "ticker": "FIDC_MICROCREDITO",
        "company_name": "FIDC Microcrédito",
        "market": "BR",
        "currency": "BRL",
        "sector": "fundos",
        "analyst": "Analista Financeiro & Crédito",
        "quantity": 1,
        "avg_price": 14565.79,
        "total_invested": 14565.79,
        "dividends_received": 0,
    },
    {
        "ticker": "ELET_FMP",
        "company_name": "BTG Eletrobrás FMP",
        "market": "BR",
        "currency": "BRL",
        "sector": "fundos",
        "analyst": "Analista de Utilities & Concessões",
        "quantity": 1,
        "avg_price": 36864.92,
        "total_invested": 36864.92,
        "dividends_received": 0,
    },
    {
        "ticker": "CAIXA",
        "company_name": "Cofrinhos",
        "market": "BR",
        "currency": "BRL",
        "sector": "caixa",
        "analyst": None,
        "quantity": 1,
        "avg_price": 91798.00,
        "total_invested": 91798.00,
        "dividends_received": 0,
    },
]


def get_client():
    """Cria cliente Supabase lendo secrets do .streamlit/secrets.toml."""
    with open(SECRETS_PATH, "rb") as f:
        secrets = tomllib.load(f)
    return create_client(secrets["supabase"]["url"], secrets["supabase"]["key"])


def seed_positions(client) -> dict[str, str]:
    """Insere posições e retorna mapa ticker → position_id."""
    all_positions = POSITIONS_BR + POSITIONS_US + POSITIONS_OTHER

    # Limpar tabela antes de inserir
    for pos in all_positions:
        client.table("positions").delete().eq("ticker", pos["ticker"]).execute()

    res = client.table("positions").insert(all_positions).execute()
    ticker_to_id = {row["ticker"]: row["id"] for row in res.data}
    print(f"  {len(res.data)} posições inseridas")
    return ticker_to_id


def seed_transactions(client, ticker_to_id: dict[str, str]) -> None:
    """Cria transação inicial BUY para cada posição."""
    all_positions = POSITIONS_BR + POSITIONS_US + POSITIONS_OTHER
    transactions = []

    for pos in all_positions:
        ticker = pos["ticker"]
        transactions.append(
            {
                "position_id": ticker_to_id[ticker],
                "ticker": ticker,
                "type": "BUY",
                "quantity": pos["quantity"],
                "price": pos["avg_price"],
                "total_value": pos["total_invested"],
                "currency": pos["currency"],
                "date": "2026-02-18",
                "notes": "Seed inicial — posição existente importada do Excel",
            }
        )

    # Limpar transações de seed anteriores
    client.table("transactions").delete().eq("notes", "Seed inicial — posição existente importada do Excel").execute()

    res = client.table("transactions").insert(transactions).execute()
    print(f"  {len(res.data)} transações inseridas")


TICKER_SECTOR = {
    "INBR32": "financeiro", "ENGI4": "utilities", "EQTL3": "utilities",
    "ALOS3": "consumo_varejo", "SUZB3": "energia_materiais", "KLBN4": "energia_materiais",
    "BRAV3": "energia_materiais", "PLPL3": "consumo_varejo", "RAPT4": "consumo_varejo",
    "GMAT3": "consumo_varejo", "MGLU3": "consumo_varejo", "UGPA3": "energia_materiais",
    "TSM": "tech_semis", "NVDA": "tech_semis", "ASML": "tech_semis",
    "MELI": "tech_semis", "GOOGL": "tech_semis", "SNPS": "tech_semis", "MU": "tech_semis",
}

# Metadados dos relatórios — PRD seção 4.6
REPORT_METADATA = {
    "oil_analysis.md": {
        "title": "Oil Commodity Analysis: A Market Drowning in Barrels but Priced for War",
        "report_type": "SECTOR",
        "tags": ["oil", "brent", "energy", "brav3"],
        "tickers_mentioned": ["BRAV3", "UGPA3"],
    },
    "relatorio_macro_rotacao.md": {
        "title": "Relatório Macro & Rotação",
        "report_type": "MACRO",
        "tags": ["selic", "rotacao", "macro", "ciclo"],
        "tickers_mentioned": ["ENGI4", "INBR32", "PLPL3", "EQTL3", "ALOS3"],
    },
    "relatorio_safra_2025_26.md": {
        "title": "Relatório Safra 2025/26",
        "report_type": "THEMATIC",
        "tags": ["agro", "safra", "commodities"],
        "tickers_mentioned": [],
    },
}

KB_DIR = Path(__file__).parent.parent / "knowledge_base"


def _extract_title(content: str) -> str:
    """Extrai o título H1 do markdown."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else "Sem título"


def _extract_summary(content: str) -> str:
    """Extrai resumo da tese ou sumário executivo."""
    patterns = [
        r"(?:RESUMO DA TESE|SUMÁRIO EXECUTIVO|SUM[ÃA]RIO EXECUTIVO).*?\n\n(.+?)(?:\n---|\n##|\n\n\n)",
        r"(?:Elevator Pitch\))\s*\n\n(.+?)(?:\n---|\n##)",
    ]
    for pat in patterns:
        match = re.search(pat, content, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            # Limitar a ~500 chars
            if len(text) > 500:
                text = text[:497] + "..."
            return text
    return ""


def _extract_analyst(content: str) -> str:
    """Extrai analista do cabeçalho."""
    match = re.search(r"\*\*Analista.*?:\*\*\s*(.+?)(?:\s{2,}|\n|\|)", content)
    return match.group(1).strip() if match else ""


def _extract_date(content: str) -> str:
    """Extrai data do cabeçalho (DD/MM/YYYY → YYYY-MM-DD)."""
    match = re.search(r"\*\*Data:\*\*\s*(\d{2}/\d{2}/\d{4})", content)
    if match:
        d, m, y = match.group(1).split("/")
        return f"{y}-{m}-{d}"
    return "2026-02-18"


def seed_deep_dives(client) -> None:
    """Lê deep dives de knowledge_base/ e popula tabela deep_dives."""
    deepdives_dir = KB_DIR / "deepdives"
    suzb3_file = KB_DIR / "reports" / "tese_suzb3_atualizada.md"

    # Limpar deep dives seeded anteriormente (version=1)
    existing = client.table("deep_dives").select("id,version").eq("version", 1).execute().data
    for row in existing:
        client.table("deep_dives").delete().eq("id", row["id"]).execute()

    records = []
    # 18 arquivos de deepdives/
    for md_file in sorted(deepdives_dir.glob("*.md")):
        ticker = md_file.stem
        content = md_file.read_text(encoding="utf-8")
        sector = TICKER_SECTOR.get(ticker, "")
        records.append({
            "ticker": ticker,
            "version": 1,
            "title": _extract_title(content),
            "analyst": _extract_analyst(content),
            "content_md": content,
            "summary": _extract_summary(content),
            "key_metrics": {},
            "tags": ["initial_deep_dive", sector],
            "date": _extract_date(content),
        })

    # SUZB3 de reports/ (PRD 4.6 nota)
    if suzb3_file.exists():
        content = suzb3_file.read_text(encoding="utf-8")
        records.append({
            "ticker": "SUZB3",
            "version": 1,
            "title": _extract_title(content),
            "analyst": _extract_analyst(content),
            "content_md": content,
            "summary": _extract_summary(content),
            "key_metrics": {},
            "tags": ["initial_deep_dive", "energia_materiais"],
            "date": _extract_date(content),
        })

    res = client.table("deep_dives").insert(records).execute()
    print(f"  {len(res.data)} deep dives inseridos")


def seed_reports(client) -> None:
    """Lê relatórios de knowledge_base/reports/ e popula tabela analysis_reports."""
    reports_dir = KB_DIR / "reports"

    # Limpar relatórios seeded anteriormente
    for meta in REPORT_METADATA.values():
        client.table("analysis_reports").delete().eq("title", meta["title"]).execute()

    records = []
    for filename, meta in REPORT_METADATA.items():
        filepath = reports_dir / filename
        if not filepath.exists():
            print(f"  AVISO: {filename} não encontrado, pulando")
            continue
        content = filepath.read_text(encoding="utf-8")
        records.append({
            "title": meta["title"],
            "report_type": meta["report_type"],
            "content_md": content,
            "summary": _extract_summary(content),
            "tickers_mentioned": meta["tickers_mentioned"],
            "tags": meta["tags"],
            "date": _extract_date(content),
        })

    if records:
        res = client.table("analysis_reports").insert(records).execute()
        print(f"  {len(res.data)} relatórios inseridos")


def main():
    print("Seed — Portfolio Cockpit")
    print("=" * 40)

    client = get_client()

    print("\n1. Positions...")
    ticker_to_id = seed_positions(client)

    print("\n2. Transactions...")
    seed_transactions(client, ticker_to_id)

    print("\n3. Deep Dives...")
    seed_deep_dives(client)

    print("\n4. Analysis Reports...")
    seed_reports(client)

    print("\nSeed concluído!")


if __name__ == "__main__":
    main()
