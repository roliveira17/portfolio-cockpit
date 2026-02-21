"""Testes para data/db.py — CRUD Supabase com MagicMock chainable client."""

from unittest.mock import MagicMock, patch


def _make_mock_client(data=None):
    """Helper: cria mock Supabase client com chain padrão."""
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = data if data is not None else []

    table_mock = MagicMock()
    client.table.return_value = table_mock

    for method in ["select", "eq", "order", "limit", "insert", "update", "delete"]:
        getattr(table_mock, method).return_value = table_mock

    table_mock.execute.return_value = mock_response
    return client


# ============================================================
# Generic helpers
# ============================================================


class TestFetchAll:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import fetch_all

        result = fetch_all("positions")
        assert result == data

    @patch("data.db.get_client")
    def test_empty_table(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import fetch_all

        result = fetch_all("positions")
        assert result == []

    @patch("data.db.get_client", side_effect=Exception("connection error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import fetch_all

        result = fetch_all("positions")
        assert result == []


class TestFetchById:
    @patch("data.db.get_client")
    def test_found(self, mock_get_client):
        data = [{"id": "123", "ticker": "INBR32"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import fetch_by_id

        result = fetch_by_id("positions", "123")
        assert result == {"id": "123", "ticker": "INBR32"}

    @patch("data.db.get_client")
    def test_not_found(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import fetch_by_id

        result = fetch_by_id("positions", "nonexistent")
        assert result is None


class TestInsertRow:
    @patch("data.db.get_client")
    def test_success(self, mock_get_client):
        inserted = {"id": "new", "ticker": "TSM"}
        mock_get_client.return_value = _make_mock_client([inserted])

        from data.db import insert_row

        result = insert_row("positions", {"ticker": "TSM"})
        assert result == inserted


class TestInsertRows:
    @patch("data.db.get_client")
    def test_batch_insert(self, mock_get_client):
        inserted = [{"id": "1", "ticker": "A"}, {"id": "2", "ticker": "B"}]
        mock_get_client.return_value = _make_mock_client(inserted)

        from data.db import insert_rows

        result = insert_rows("positions", [{"ticker": "A"}, {"ticker": "B"}])
        assert len(result) == 2


class TestUpdateRow:
    @patch("data.db.get_client")
    def test_success(self, mock_get_client):
        updated = {"id": "123", "ticker": "INBR32", "quantity": 2000}
        mock_get_client.return_value = _make_mock_client([updated])

        from data.db import update_row

        result = update_row("positions", "123", {"quantity": 2000})
        assert result["quantity"] == 2000


class TestDeleteRow:
    @patch("data.db.get_client")
    def test_success(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import delete_row

        # Should not raise
        delete_row("positions", "123")


# ============================================================
# Positions
# ============================================================


class TestGetPositions:
    @patch("data.db.get_client")
    def test_active_only(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32", "is_active": True}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_positions

        result = get_positions(active_only=True)
        assert len(result) == 1

    @patch("data.db.get_client")
    def test_all_positions(self, mock_get_client):
        data = [
            {"id": "1", "ticker": "INBR32", "is_active": True},
            {"id": "2", "ticker": "XXX", "is_active": False},
        ]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_positions

        result = get_positions(active_only=False)
        assert len(result) == 2

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_positions

        result = get_positions()
        assert result == []


class TestGetPositionByTicker:
    @patch("data.db.get_client")
    def test_found(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_position_by_ticker

        result = get_position_by_ticker("INBR32")
        assert result["ticker"] == "INBR32"

    @patch("data.db.get_client")
    def test_not_found(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import get_position_by_ticker

        result = get_position_by_ticker("XXX")
        assert result is None


# ============================================================
# Transactions
# ============================================================


class TestGetTransactions:
    @patch("data.db.get_client")
    def test_all_transactions(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32", "type": "BUY"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_transactions

        result = get_transactions()
        assert len(result) == 1

    @patch("data.db.get_client")
    def test_filtered_by_ticker(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32", "type": "BUY"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_transactions

        result = get_transactions(ticker="INBR32")
        assert len(result) == 1


# ============================================================
# Theses
# ============================================================


class TestGetTheses:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32", "status": "GREEN"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_theses

        result = get_theses()
        assert len(result) == 1

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_theses

        result = get_theses()
        assert result == []


class TestGetThesisByTicker:
    @patch("data.db.get_client")
    def test_found(self, mock_get_client):
        data = [{"id": "1", "ticker": "INBR32", "status": "GREEN"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_thesis_by_ticker

        result = get_thesis_by_ticker("INBR32")
        assert result["status"] == "GREEN"

    @patch("data.db.get_client")
    def test_not_found(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import get_thesis_by_ticker

        result = get_thesis_by_ticker("XXX")
        assert result is None


# ============================================================
# Catalysts
# ============================================================


class TestGetUpcomingCatalysts:
    @patch("data.db.get_client")
    def test_returns_limited(self, mock_get_client):
        data = [{"id": "1", "ticker": "MELI", "completed": False}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_upcoming_catalysts

        result = get_upcoming_catalysts(limit=5)
        assert len(result) == 1

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_upcoming_catalysts

        result = get_upcoming_catalysts()
        assert result == []


class TestGetCatalystsByTicker:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [
            {"id": "1", "ticker": "INBR32", "description": "Q4"},
            {"id": "2", "ticker": "INBR32", "description": "Selic"},
        ]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_catalysts_by_ticker

        result = get_catalysts_by_ticker("INBR32")
        assert len(result) == 2


class TestGetAllCatalysts:
    @patch("data.db.get_client")
    def test_exclude_completed(self, mock_get_client):
        data = [{"id": "1", "completed": False}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_all_catalysts

        result = get_all_catalysts(include_completed=False)
        assert len(result) == 1

    @patch("data.db.get_client")
    def test_include_completed(self, mock_get_client):
        data = [
            {"id": "1", "completed": False},
            {"id": "2", "completed": True},
        ]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_all_catalysts

        result = get_all_catalysts(include_completed=True)
        assert len(result) == 2


# ============================================================
# Deep Dives
# ============================================================


class TestGetDeepDivesByTicker:
    @patch("data.db.get_client")
    def test_multiple_versions(self, mock_get_client):
        data = [
            {"id": "2", "ticker": "INBR32", "version": 2},
            {"id": "1", "ticker": "INBR32", "version": 1},
        ]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_deep_dives_by_ticker

        result = get_deep_dives_by_ticker("INBR32")
        assert len(result) == 2


class TestGetLatestDeepDive:
    @patch("data.db.get_client")
    def test_returns_latest(self, mock_get_client):
        data = [{"id": "2", "ticker": "INBR32", "version": 2}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_latest_deep_dive

        result = get_latest_deep_dive("INBR32")
        assert result["version"] == 2

    @patch("data.db.get_client")
    def test_not_found(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import get_latest_deep_dive

        result = get_latest_deep_dive("XXX")
        assert result is None


class TestGetAllDeepDives:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [{"id": "1"}, {"id": "2"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_all_deep_dives

        result = get_all_deep_dives()
        assert len(result) == 2

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_all_deep_dives

        result = get_all_deep_dives()
        assert result == []


class TestGetNextDeepDiveVersion:
    @patch("data.db.get_deep_dives_by_ticker")
    def test_with_existing(self, mock_dives):
        mock_dives.return_value = [{"version": 3}, {"version": 2}, {"version": 1}]

        from data.db import get_next_deep_dive_version

        assert get_next_deep_dive_version("INBR32") == 4

    @patch("data.db.get_deep_dives_by_ticker")
    def test_without_existing(self, mock_dives):
        mock_dives.return_value = []

        from data.db import get_next_deep_dive_version

        assert get_next_deep_dive_version("NEW_TICKER") == 1


# ============================================================
# Analysis Reports
# ============================================================


class TestGetAnalysisReports:
    @patch("data.db.get_client")
    def test_all_reports(self, mock_get_client):
        data = [{"id": "1", "report_type": "MACRO"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_analysis_reports

        result = get_analysis_reports()
        assert len(result) == 1

    @patch("data.db.get_client")
    def test_filtered_by_type(self, mock_get_client):
        data = [{"id": "1", "report_type": "SECTOR"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_analysis_reports

        result = get_analysis_reports(report_type="SECTOR")
        assert len(result) == 1

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_analysis_reports

        result = get_analysis_reports()
        assert result == []


# ============================================================
# Portfolio Snapshots
# ============================================================


class TestGetPortfolioSnapshots:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [{"id": "1", "date": "2026-02-18"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_portfolio_snapshots

        result = get_portfolio_snapshots()
        assert len(result) == 1

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_portfolio_snapshots

        result = get_portfolio_snapshots()
        assert result == []


class TestGetLatestPortfolioSnapshot:
    @patch("data.db.get_client")
    def test_returns_latest(self, mock_get_client):
        data = [{"id": "1", "date": "2026-02-20", "total_value_brl": 514000}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_latest_portfolio_snapshot

        result = get_latest_portfolio_snapshot()
        assert result["total_value_brl"] == 514000

    @patch("data.db.get_client")
    def test_empty_returns_none(self, mock_get_client):
        mock_get_client.return_value = _make_mock_client([])

        from data.db import get_latest_portfolio_snapshot

        result = get_latest_portfolio_snapshot()
        assert result is None

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_none(self, mock_get_client):
        from data.db import get_latest_portfolio_snapshot

        result = get_latest_portfolio_snapshot()
        assert result is None


class TestSavePortfolioSnapshot:
    @patch("data.db.insert_row")
    def test_delegates_to_insert_row(self, mock_insert):
        mock_insert.return_value = {"id": "new", "date": "2026-02-20"}

        from data.db import save_portfolio_snapshot

        save_portfolio_snapshot({"date": "2026-02-20", "total_value_brl": 514000})
        mock_insert.assert_called_once_with("portfolio_snapshots", {"date": "2026-02-20", "total_value_brl": 514000})


# ============================================================
# Chat helpers
# ============================================================


class TestUpsertThesis:
    @patch("data.db.update_row")
    @patch("data.db.get_thesis_by_ticker")
    def test_existing_thesis_updates(self, mock_get, mock_update):
        mock_get.return_value = {"id": "123", "ticker": "INBR32"}
        mock_update.return_value = {"id": "123", "ticker": "INBR32", "status": "GREEN"}

        from data.db import upsert_thesis

        result = upsert_thesis("INBR32", {"status": "GREEN"})
        mock_update.assert_called_once()
        assert result["status"] == "GREEN"

    @patch("data.db.insert_row")
    @patch("data.db.get_thesis_by_ticker")
    def test_new_thesis_inserts(self, mock_get, mock_insert):
        mock_get.return_value = None
        mock_insert.return_value = {"id": "new", "ticker": "NEW", "status": "YELLOW"}

        from data.db import upsert_thesis

        upsert_thesis("NEW", {"status": "YELLOW"})
        mock_insert.assert_called_once()

    @patch("data.db.get_thesis_by_ticker", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get):
        from data.db import upsert_thesis

        result = upsert_thesis("INBR32", {"status": "GREEN"})
        assert result == {}


class TestUpdatePositionFields:
    @patch("data.db.update_row")
    @patch("data.db.get_position_by_ticker")
    def test_found_updates(self, mock_get, mock_update):
        mock_get.return_value = {"id": "123", "ticker": "INBR32"}
        mock_update.return_value = {"id": "123", "quantity": 2000}

        from data.db import update_position_fields

        result = update_position_fields("INBR32", {"quantity": 2000})
        assert result["quantity"] == 2000

    @patch("data.db.get_position_by_ticker")
    def test_not_found_returns_none(self, mock_get):
        mock_get.return_value = None

        from data.db import update_position_fields

        result = update_position_fields("XXX", {"quantity": 100})
        assert result is None

    @patch("data.db.get_position_by_ticker", side_effect=Exception("db error"))
    def test_exception_returns_none(self, mock_get):
        from data.db import update_position_fields

        result = update_position_fields("INBR32", {})
        assert result is None


class TestGetAllDeepDiveSummaries:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [{"ticker": "INBR32", "title": "Deep Dive", "version": 1}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_all_deep_dive_summaries

        result = get_all_deep_dive_summaries()
        assert len(result) == 1

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_all_deep_dive_summaries

        result = get_all_deep_dive_summaries()
        assert result == []


class TestGetAllThesisSummaries:
    @patch("data.db.get_client")
    def test_returns_list(self, mock_get_client):
        data = [{"ticker": "INBR32", "status": "GREEN", "conviction": "HIGH"}]
        mock_get_client.return_value = _make_mock_client(data)

        from data.db import get_all_thesis_summaries

        result = get_all_thesis_summaries()
        assert len(result) == 1

    @patch("data.db.get_client", side_effect=Exception("db error"))
    def test_exception_returns_empty(self, mock_get_client):
        from data.db import get_all_thesis_summaries

        result = get_all_thesis_summaries()
        assert result == []
