"""Métricas de performance: retornos, Sharpe, Sortino, drawdown, volatilidade, beta."""

import numpy as np
import pandas as pd


def calc_portfolio_returns(
    price_history: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series | None:
    """Calcula retornos diários ponderados do portfólio.

    Args:
        price_history: DataFrame com DatetimeIndex e colunas por ticker (preços de fechamento).
        weights: {ticker: peso_decimal} (ex: {"INBR32": 0.17, "ENGI4": 0.09}).

    Returns:
        Series de retornos diários do portfólio (float, não %).
    """
    if price_history is None or price_history.empty:
        return None

    # Filtrar apenas tickers presentes no histórico e nos pesos
    common = [t for t in weights if t in price_history.columns]
    if not common:
        return None

    returns = price_history[common].pct_change().dropna()
    if returns.empty:
        return None

    # Normalizar pesos para somar 1.0
    w = np.array([weights[t] for t in common])
    w_sum = w.sum()
    if w_sum <= 0:
        return None
    w = w / w_sum

    portfolio_returns = returns[common].dot(w)
    portfolio_returns.name = "portfolio"
    return portfolio_returns


def calc_cumulative_returns(returns: pd.Series) -> pd.Series | None:
    """Converte retornos diários em retornos acumulados (base 1.0)."""
    if returns is None or returns.empty:
        return None
    return (1 + returns).cumprod()


def calc_sharpe_ratio(
    returns: pd.Series,
    risk_free_annual: float = 0.1325,
    trading_days: int = 252,
) -> float | None:
    """Sharpe ratio = (retorno_anualizado - risk_free) / volatilidade_anualizada."""
    if returns is None or len(returns) < 2:
        return None

    annual_return = returns.mean() * trading_days
    annual_vol = returns.std() * np.sqrt(trading_days)
    if annual_vol == 0:
        return None
    return (annual_return - risk_free_annual) / annual_vol


def calc_sortino_ratio(
    returns: pd.Series,
    risk_free_annual: float = 0.1325,
    trading_days: int = 252,
) -> float | None:
    """Sortino ratio usando apenas desvio negativo (downside deviation)."""
    if returns is None or len(returns) < 2:
        return None

    annual_return = returns.mean() * trading_days
    downside = returns[returns < 0]
    if downside.empty:
        return None
    downside_std = downside.std() * np.sqrt(trading_days)
    if downside_std == 0:
        return None
    return (annual_return - risk_free_annual) / downside_std


def calc_max_drawdown(returns: pd.Series) -> float | None:
    """Drawdown máximo como valor negativo (ex: -0.15 para -15%)."""
    dd = calc_drawdown_series(returns)
    if dd is None or dd.empty:
        return None
    return float(dd.min())


def calc_drawdown_series(returns: pd.Series) -> pd.Series | None:
    """Série de drawdown ao longo do tempo (para gráfico de área)."""
    if returns is None or returns.empty:
        return None

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    drawdown.name = "drawdown"
    return drawdown


def calc_volatility(
    returns: pd.Series,
    window: int = 30,
    trading_days: int = 252,
) -> float | None:
    """Volatilidade anualizada dos últimos `window` dias de negociação."""
    if returns is None or len(returns) < window:
        return None
    recent = returns.tail(window)
    return float(recent.std() * np.sqrt(trading_days))


def calc_beta_vs_benchmark(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float | None:
    """Beta = Cov(portfolio, benchmark) / Var(benchmark)."""
    if portfolio_returns is None or benchmark_returns is None:
        return None

    # Alinhar por índice
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    if len(aligned) < 10:
        return None

    cov = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
    var = aligned.iloc[:, 1].var()
    if var == 0:
        return None
    return cov / var
