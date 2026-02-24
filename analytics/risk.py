"""Análise de risco: VaR, stress tests, cenários pré-definidos."""

import numpy as np
import pandas as pd

from utils.constants import FACTOR_SENSITIVITIES

# ============================================================
# Cenários pré-definidos — PRD seção 6.5
# ============================================================

PREDEFINED_SCENARIOS = {
    "Estagflação": {
        "selic_1pp": 2.0,
        "usdbrl_10pct": 15.0,
        "brent_10pct": 20.0,
        "ibov_10pct": -15.0,
    },
    "Risk-off Global": {
        "selic_1pp": 0.5,
        "usdbrl_10pct": 10.0,
        "brent_10pct": -25.0,
        "ibov_10pct": -20.0,
    },
    "Selic Hawkish": {
        "selic_1pp": 3.0,
        "usdbrl_10pct": -5.0,
        "brent_10pct": 0.0,
        "ibov_10pct": -10.0,
    },
    "Bull China": {
        "selic_1pp": -0.5,
        "usdbrl_10pct": -8.0,
        "brent_10pct": 15.0,
        "ibov_10pct": 10.0,
    },
}

# Escala de cada fator: as sensibilidades são calibradas "por unidade"
# selic_1pp → sensibilidade por 1pp, shock em pp
# usdbrl_10pct → sensibilidade por 10%, shock em %
# brent_10pct → sensibilidade por 10%, shock em %
# ibov_10pct → beta, sensibilidade por 10%, shock em %
FACTOR_SCALE = {
    "selic_1pp": 1.0,
    "usdbrl_10pct": 10.0,
    "brent_10pct": 10.0,
    "ibov_10pct": 10.0,
}


# ============================================================
# VaR
# ============================================================


def calc_var_historical(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float | None:
    """VaR histórico ao nível de confiança dado.

    Retorna valor negativo representando a perda (ex: -0.025 para -2.5%).
    """
    if returns is None or len(returns) < 20:
        return None
    percentile = (1 - confidence) * 100
    return float(np.percentile(returns.dropna(), percentile))


# ============================================================
# Stress Tests
# ============================================================


def calc_stress_test_portfolio(
    portfolio_df: pd.DataFrame,
    shocks: dict[str, float],
) -> dict:
    """Aplica choques macro ao portfólio usando FACTOR_SENSITIVITIES.

    Args:
        portfolio_df: Output de build_portfolio_df().
        shocks: {factor_key: magnitude} (ex: {"selic_1pp": 1.5, "usdbrl_10pct": 10.0}).

    Returns:
        dict com total_impact_pct, total_impact_brl, new_total_brl e per_position.
    """
    total_value = portfolio_df["current_value_brl"].sum()
    if total_value <= 0:
        return {"total_impact_pct": 0, "total_impact_brl": 0, "new_total_brl": 0, "per_position": []}

    per_position = []
    total_impact_brl = 0.0

    for _, row in portfolio_df.iterrows():
        ticker = row["ticker"]
        value_brl = row["current_value_brl"] or 0

        # Somar impacto de todos os fatores
        position_impact_pct = 0.0
        for factor, shock_magnitude in shocks.items():
            sensitivity = FACTOR_SENSITIVITIES.get(factor, {}).get(ticker, 0)
            scale = FACTOR_SCALE.get(factor, 1.0)
            # impact = sensibilidade × (shock / escala)
            position_impact_pct += sensitivity * (shock_magnitude / scale)

        # Guard against NaN/inf from bad data
        if not np.isfinite(position_impact_pct):
            position_impact_pct = 0.0

        impact_brl = value_brl * position_impact_pct
        total_impact_brl += impact_brl

        per_position.append(
            {
                "ticker": ticker,
                "current_value_brl": round(value_brl, 2),
                "impact_pct": round(position_impact_pct * 100, 2),
                "impact_brl": round(impact_brl, 2),
                "new_value_brl": round(value_brl + impact_brl, 2),
            }
        )

    total_impact_pct = (total_impact_brl / total_value) * 100

    # Guard against NaN/inf from bad data
    if not np.isfinite(total_impact_pct):
        total_impact_pct = 0.0

    return {
        "total_impact_pct": round(total_impact_pct, 2),
        "total_impact_brl": round(total_impact_brl, 2),
        "new_total_brl": round(total_value + total_impact_brl, 2),
        "per_position": per_position,
    }


def calc_stress_scenario(
    portfolio_df: pd.DataFrame,
    scenario_name: str,
) -> dict:
    """Aplica cenário pré-definido. Retorna mesma estrutura que calc_stress_test_portfolio."""
    shocks = PREDEFINED_SCENARIOS.get(scenario_name, {})
    return calc_stress_test_portfolio(portfolio_df, shocks)


def get_predefined_scenarios() -> dict[str, dict]:
    """Retorna dicionário de cenários pré-definidos com seus shocks."""
    return PREDEFINED_SCENARIOS.copy()
