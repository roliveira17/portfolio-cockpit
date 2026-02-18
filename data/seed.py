"""Popular banco de dados com dados iniciais do portfólio (PRD seção 4)."""

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


def main():
    print("Seed — Portfolio Cockpit")
    print("=" * 40)

    client = get_client()

    print("\n1. Positions...")
    ticker_to_id = seed_positions(client)

    print("\n2. Transactions...")
    seed_transactions(client, ticker_to_id)

    print("\nSeed concluído!")


if __name__ == "__main__":
    main()
