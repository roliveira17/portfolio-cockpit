"""Testes para data/seed.py — funções de extração puras (sem I/O)."""

import pytest

from data.seed import (
    _extract_analyst,
    _extract_conviction,
    _extract_date,
    _extract_field_regex,
    _extract_growth_drivers,
    _extract_kill_switches,
    _extract_moat_rating,
    _extract_moat_trend,
    _extract_prices,
    _extract_summary,
    _extract_thesis_status,
    _extract_title,
    _extract_usd_prices,
    _fix_encoding,
    _parse_brl_number,
)

# ============================================================
# _fix_encoding
# ============================================================


class TestFixEncoding:
    def test_normal_text_unchanged(self):
        assert _fix_encoding("Hello World") == "Hello World"

    def test_double_encoded_utf8(self):
        # "análise" double-encoded as latin1
        double_encoded = "análise".encode("utf-8").decode("latin-1")
        assert _fix_encoding(double_encoded) == "análise"

    def test_already_correct_returns_same(self):
        assert _fix_encoding("análise") == "análise"


# ============================================================
# _extract_field_regex
# ============================================================


class TestExtractFieldRegex:
    def test_match_found(self):
        content = "ROIC atual: 12.5%"
        result = _extract_field_regex(content, r"ROIC.*?([\d.]+)%")
        assert result == "12.5"

    def test_no_match_returns_default(self):
        result = _extract_field_regex("nada aqui", r"ROIC.*?([\d.]+)%", default="N/A")
        assert result == "N/A"

    def test_no_match_returns_none(self):
        result = _extract_field_regex("nada aqui", r"ROIC.*?([\d.]+)%")
        assert result is None


# ============================================================
# _extract_title
# ============================================================


class TestExtractTitle:
    def test_h1_deep_dive(self):
        content = "# DEEP DIVE — INBR32 — Inter & Co\n\nConteúdo..."
        assert _extract_title(content) == "DEEP DIVE — INBR32 — Inter & Co"

    def test_h1_generic(self):
        content = "# Relatório Macro\n\nConteúdo..."
        assert _extract_title(content) == "Relatório Macro"

    def test_no_h1_returns_default(self):
        content = "Apenas texto sem heading"
        assert _extract_title(content) == "Sem título"

    def test_h2_not_matched(self):
        content = "## Subtítulo\n\nConteúdo..."
        assert _extract_title(content) == "Sem título"


# ============================================================
# _extract_summary
# ============================================================


class TestExtractSummary:
    def test_resumo_da_tese_section(self):
        content = """# Título

## RESUMO DA TESE

A empresa é líder no setor.

---

## Outro
"""
        result = _extract_summary(content)
        assert "líder" in result

    def test_sumario_executivo(self):
        content = """# Título

## SUMÁRIO EXECUTIVO

Resumo executivo da análise.

---
"""
        result = _extract_summary(content)
        assert "executivo" in result

    def test_absent_returns_empty(self):
        content = "# Título\n\nSem seção de resumo"
        assert _extract_summary(content) == ""

    def test_truncated_at_500_chars(self):
        long_text = "A" * 600
        content = f"# Título\n\n## RESUMO DA TESE\n\n{long_text}\n\n---"
        result = _extract_summary(content)
        assert len(result) <= 500


# ============================================================
# _extract_analyst
# ============================================================


class TestExtractAnalyst:
    def test_found(self):
        content = "**Analista responsável:** João Silva  \n**Data:** 01/02/2026"
        result = _extract_analyst(content)
        assert result == "João Silva"

    def test_absent_returns_empty(self):
        content = "# Título\nSem analista"
        assert _extract_analyst(content) == ""


# ============================================================
# _extract_date
# ============================================================


class TestExtractDate:
    def test_dd_mm_yyyy_format(self):
        content = "**Data:** 18/02/2026\n"
        assert _extract_date(content) == "2026-02-18"

    def test_absent_returns_default(self):
        content = "# Título\nSem data"
        assert _extract_date(content) == "2026-02-18"


# ============================================================
# _extract_thesis_status
# ============================================================


class TestExtractThesisStatus:
    def test_green_emoji(self):
        assert _extract_thesis_status("🟢 Tese ativa") == "GREEN"

    def test_green_text(self):
        assert _extract_thesis_status("Status: Ativa e confirmada") == "GREEN"

    def test_red_emoji(self):
        assert _extract_thesis_status("🔴 ENCERRAMENTO") == "RED"

    def test_red_text(self):
        assert _extract_thesis_status("RECOMENDAÇÃO: ENCERRAMENTO") == "RED"

    def test_yellow_text(self):
        assert _extract_thesis_status("Status: Em Revisão") == "YELLOW"

    def test_default_yellow(self):
        assert _extract_thesis_status("Sem status claro") == "YELLOW"


# ============================================================
# _extract_conviction
# ============================================================


class TestExtractConviction:
    def test_high(self):
        assert _extract_conviction("Convicção: **ALTA**") == "HIGH"

    def test_high_english(self):
        assert _extract_conviction("Conviction: HIGH") == "HIGH"

    def test_low(self):
        assert _extract_conviction("Convicção: BAIXA") == "LOW"

    def test_medium(self):
        assert _extract_conviction("Convicção: Média") == "MEDIUM"

    def test_absent_returns_medium(self):
        assert _extract_conviction("Sem convicção") == "MEDIUM"


# ============================================================
# _extract_moat_rating
# ============================================================


class TestExtractMoatRating:
    def test_strong(self):
        assert _extract_moat_rating("Moat: STRONG") == "STRONG"

    def test_forte(self):
        assert _extract_moat_rating("Moat econômico: Forte") == "STRONG"

    def test_weak(self):
        assert _extract_moat_rating("Moat: WEAK") == "WEAK"

    def test_fraco(self):
        assert _extract_moat_rating("Moat: Fraco") == "WEAK"

    def test_none(self):
        assert _extract_moat_rating("Moat: INEXISTENTE") == "NONE"

    def test_moderate_default(self):
        assert _extract_moat_rating("Moat: MODERATE") == "MODERATE"

    def test_absent_returns_moderate(self):
        assert _extract_moat_rating("Sem informação de moat") == "MODERATE"


# ============================================================
# _extract_moat_trend
# ============================================================


class TestExtractMoatTrend:
    def test_widening(self):
        assert _extract_moat_trend("Durabilidade: Ampliando") == "WIDENING"

    def test_narrowing(self):
        assert _extract_moat_trend("Durabilidade: Estreitando") == "NARROWING"

    def test_stable(self):
        assert _extract_moat_trend("Durabilidade: Estável") == "STABLE"

    def test_absent_returns_stable(self):
        assert _extract_moat_trend("Sem informação") == "STABLE"


# ============================================================
# _parse_brl_number
# ============================================================


class TestParseBrlNumber:
    def test_decimal_comma(self):
        assert _parse_brl_number("58,25") == pytest.approx(58.25)

    def test_decimal_dot(self):
        assert _parse_brl_number("58.25") == pytest.approx(5825.0)

    def test_thousands_dot(self):
        # "1.234,56" → 1234.56
        assert _parse_brl_number("1.234,56") == pytest.approx(1234.56)

    def test_none_returns_none(self):
        assert _parse_brl_number(None) is None

    def test_empty_returns_none(self):
        assert _parse_brl_number("") is None

    def test_invalid_returns_none(self):
        assert _parse_brl_number("abc") is None


# ============================================================
# _extract_prices
# ============================================================


class TestExtractPrices:
    def test_all_prices_found(self):
        content = """
**Preço-alvo ponderado:** R$58,00
Bull case: R$70,00
Base case: R$55,00
Bear case: R$40,00
"""
        result = _extract_prices(content)
        assert result["target_price"] == pytest.approx(58.0)
        assert result["bull_case_price"] == pytest.approx(70.0)
        assert result["base_case_price"] == pytest.approx(55.0)
        assert result["bear_case_price"] == pytest.approx(40.0)

    def test_missing_prices(self):
        result = _extract_prices("Sem preços")
        assert result["target_price"] is None
        assert result["bull_case_price"] is None


# ============================================================
# _extract_usd_prices
# ============================================================


class TestExtractUsdPrices:
    def test_usd_prices_found(self):
        content = """
**Preço-alvo ponderado:** $450.00
Bull case: $550.00
Base case: $420.00
Bear case: $350.00
"""
        result = _extract_usd_prices(content)
        assert result["target_price"] is not None
        assert result["bull_case_price"] is not None


# ============================================================
# _extract_kill_switches
# ============================================================


class TestExtractKillSwitches:
    def test_kill_switches_found(self):
        content = """## KILL SWITCH
1. KILL SWITCH 1: ROIC cair abaixo de WACC por 2 trimestres consecutivos
2. KILL SWITCH 2: Inadimplencia subir acima de 5% da carteira total
"""
        result = _extract_kill_switches(content)
        assert len(result) >= 1

    def test_ks_format(self):
        content = """## KILL SWITCH
- KS-1: Perda de market share significativa por dois trimestres
- KS-2: ROIC abaixo do WACC por dois trimestres seguidos
"""
        result = _extract_kill_switches(content)
        assert len(result) >= 1

    def test_empty_when_absent(self):
        result = _extract_kill_switches("Sem kill switches")
        assert result == []


# ============================================================
# _extract_growth_drivers
# ============================================================


class TestExtractGrowthDrivers:
    def test_growth_drivers_found(self):
        content = """
## GROWTH DRIVERS
1. **Expansão digital** — crescimento de 30% a.a.
2. **Crédito consignado** — nova vertical
3. **Cross-selling** — base de 30M clientes
"""
        result = _extract_growth_drivers(content)
        assert len(result) >= 2

    def test_empty_when_absent(self):
        result = _extract_growth_drivers("Sem growth drivers")
        assert result == []

    def test_vetores_de_crescimento(self):
        content = """
## VETORES DE CRESCIMENTO
1. **Fator A** — descrição
2. **Fator B** — descrição
"""
        result = _extract_growth_drivers(content)
        assert len(result) >= 1
