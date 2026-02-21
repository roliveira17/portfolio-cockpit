"""Testes para módulos de dados de mercado (Sprint 6)."""

from utils.constants import (
    COMMODITIES_TICKERS,
    GLOBAL_INDICES,
    REGION_LABELS,
    TREASURY_MATURITIES,
)

# ============================================================
# Testes de estrutura de constantes
# ============================================================


class TestGlobalIndicesConstants:
    """Verifica integridade das constantes de índices globais."""

    def test_regions_have_indices(self):
        for region in GLOBAL_INDICES:
            assert len(GLOBAL_INDICES[region]) > 0, f"Região {region} sem índices"

    def test_all_regions_have_labels(self):
        for region in GLOBAL_INDICES:
            assert region in REGION_LABELS, f"Região {region} sem label"

    def test_index_structure(self):
        for region, indices in GLOBAL_INDICES.items():
            for idx in indices:
                assert "ticker" in idx, f"Índice sem ticker em {region}"
                assert "name" in idx, f"Índice sem name em {region}"
                assert "country" in idx, f"Índice sem country em {region}"


class TestCommoditiesConstants:
    """Verifica integridade das constantes de commodities."""

    def test_commodities_not_empty(self):
        assert len(COMMODITIES_TICKERS) > 0

    def test_commodity_structure(self):
        for comm in COMMODITIES_TICKERS:
            assert "ticker" in comm
            assert "name" in comm
            assert "unit" in comm
            assert "category" in comm

    def test_commodity_categories(self):
        categories = {c["category"] for c in COMMODITIES_TICKERS}
        assert "energy" in categories
        assert "metals" in categories


class TestTreasuryConstants:
    """Verifica integridade das constantes de Treasury."""

    def test_maturities_not_empty(self):
        assert len(TREASURY_MATURITIES) > 0

    def test_maturity_structure(self):
        for mat in TREASURY_MATURITIES:
            assert "tag" in mat
            assert "label" in mat
            assert "years" in mat
            assert mat["years"] > 0

    def test_key_maturities_present(self):
        labels = {m["label"] for m in TREASURY_MATURITIES}
        assert "1A" in labels
        assert "10A" in labels
        assert "30A" in labels


# ============================================================
# Testes de parsing (Treasury XML)
# ============================================================


class TestTreasuryXmlParsing:
    """Testa parsing de XML do Treasury.gov."""

    SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
          xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
      <entry>
        <content type="application/xml">
          <m:properties>
            <d:NEW_DATE>2026-02-20T00:00:00</d:NEW_DATE>
            <d:BC_1MONTH>4.530</d:BC_1MONTH>
            <d:BC_3MONTH>4.320</d:BC_3MONTH>
            <d:BC_1YEAR>4.150</d:BC_1YEAR>
            <d:BC_10YEAR>4.520</d:BC_10YEAR>
            <d:BC_30YEAR>4.710</d:BC_30YEAR>
          </m:properties>
        </content>
      </entry>
    </feed>"""

    def test_parse_treasury_xml(self):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(self.SAMPLE_XML, "xml")
        entries = soup.find_all("entry")
        assert len(entries) == 1

        entry = entries[0]
        date_elem = entry.find("d:NEW_DATE")
        assert date_elem is not None
        assert date_elem.text.startswith("2026-02-20")

        ten_year = entry.find("BC_10YEAR")
        assert ten_year is not None
        assert float(ten_year.text) == 4.520


# ============================================================
# Testes de cache_info
# ============================================================


class TestCacheInfo:
    """Testa módulo de freshness tracking (sem Streamlit)."""

    def test_imports(self):
        """Verifica que o módulo pode ser importado."""
        from utils.cache_info import get_fetch_time, record_fetch_time

        assert callable(record_fetch_time)
        assert callable(get_fetch_time)
