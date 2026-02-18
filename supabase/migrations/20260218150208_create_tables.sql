-- ============================================================
-- Portfolio Cockpit — Schema inicial (8 tabelas)
-- Ref: docs/specs/PRD.md seção 3
-- ============================================================

-- 1. positions
CREATE TABLE positions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker text NOT NULL,
    company_name text NOT NULL,
    market text NOT NULL CHECK (market IN ('BR', 'US')),
    currency text NOT NULL CHECK (currency IN ('BRL', 'USD')),
    sector text NOT NULL CHECK (sector IN (
        'energia_materiais', 'utilities', 'consumo_varejo',
        'tech_semis', 'financeiro', 'fundos', 'caixa'
    )),
    analyst text,
    quantity decimal NOT NULL DEFAULT 0,
    avg_price decimal NOT NULL DEFAULT 0,
    total_invested decimal NOT NULL DEFAULT 0,
    dividends_received decimal NOT NULL DEFAULT 0,
    target_weight decimal DEFAULT 0,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2. transactions
CREATE TABLE transactions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    position_id uuid REFERENCES positions(id) ON DELETE CASCADE,
    ticker text NOT NULL,
    type text NOT NULL CHECK (type IN ('BUY', 'SELL', 'DIVIDEND')),
    quantity decimal NOT NULL,
    price decimal NOT NULL,
    total_value decimal NOT NULL,
    currency text NOT NULL CHECK (currency IN ('BRL', 'USD')),
    date date NOT NULL,
    notes text,
    created_at timestamptz DEFAULT now()
);

-- 3. theses
CREATE TABLE theses (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    position_id uuid REFERENCES positions(id) ON DELETE CASCADE,
    ticker text NOT NULL,
    status text NOT NULL CHECK (status IN ('GREEN', 'YELLOW', 'RED')) DEFAULT 'GREEN',
    conviction text NOT NULL CHECK (conviction IN ('HIGH', 'MEDIUM', 'LOW')) DEFAULT 'MEDIUM',
    summary text,
    moat_rating text CHECK (moat_rating IN ('STRONG', 'MODERATE', 'WEAK', 'NONE')),
    moat_trend text CHECK (moat_trend IN ('WIDENING', 'STABLE', 'NARROWING')),
    growth_drivers jsonb DEFAULT '[]'::jsonb,
    bull_case_price decimal,
    base_case_price decimal,
    bear_case_price decimal,
    target_price decimal,
    kill_switches jsonb DEFAULT '[]'::jsonb,
    catalysts jsonb DEFAULT '[]'::jsonb,
    key_risks jsonb DEFAULT '[]'::jsonb,
    roic_current decimal,
    wacc_estimated decimal,
    last_review date,
    next_review date,
    review_trigger text,
    notes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 4. catalysts
CREATE TABLE catalysts (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker text NOT NULL,
    description text NOT NULL,
    expected_date date,
    impact text CHECK (impact IN ('HIGH', 'MEDIUM', 'LOW')),
    category text CHECK (category IN ('EARNINGS', 'REGULATORY', 'MACRO', 'CORPORATE', 'OTHER')),
    completed boolean NOT NULL DEFAULT false,
    outcome_notes text,
    created_at timestamptz DEFAULT now()
);

-- 5. macro_snapshots
CREATE TABLE macro_snapshots (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    date date NOT NULL,
    selic decimal,
    ipca_12m decimal,
    usd_brl decimal,
    dxy decimal,
    ibov decimal,
    sp500 decimal,
    vix decimal,
    brent decimal,
    cellulose_bhkp decimal,
    treasury_10y decimal,
    di_jan27 decimal,
    cds_brazil_5y decimal,
    created_at timestamptz DEFAULT now()
);

-- 6. deep_dives
CREATE TABLE deep_dives (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker text NOT NULL,
    version integer NOT NULL DEFAULT 1,
    title text,
    analyst text,
    content_md text,
    summary text,
    thesis_status_at_time text CHECK (thesis_status_at_time IN ('GREEN', 'YELLOW', 'RED')),
    conviction_at_time text CHECK (conviction_at_time IN ('HIGH', 'MEDIUM', 'LOW')),
    target_price_at_time decimal,
    current_price_at_time decimal,
    key_metrics jsonb DEFAULT '{}'::jsonb,
    key_changes text,
    tags text[] DEFAULT '{}',
    date date,
    created_at timestamptz DEFAULT now(),
    UNIQUE (ticker, version)
);

-- 7. analysis_reports
CREATE TABLE analysis_reports (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    title text NOT NULL,
    report_type text NOT NULL CHECK (report_type IN ('MACRO', 'SECTOR', 'THEMATIC', 'PORTFOLIO_REVIEW')),
    content_md text,
    summary text,
    tickers_mentioned text[] DEFAULT '{}',
    tags text[] DEFAULT '{}',
    date date,
    created_at timestamptz DEFAULT now()
);

-- 8. portfolio_snapshots
CREATE TABLE portfolio_snapshots (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    date date NOT NULL,
    total_value_brl decimal,
    total_value_usd decimal,
    cash_brl decimal,
    positions_data jsonb DEFAULT '[]'::jsonb,
    ibov_value decimal,
    cdi_accumulated decimal,
    created_at timestamptz DEFAULT now()
);

-- ============================================================
-- Índices úteis
-- ============================================================
CREATE INDEX idx_positions_ticker ON positions(ticker);
CREATE INDEX idx_positions_sector ON positions(sector);
CREATE INDEX idx_transactions_position ON transactions(position_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_theses_ticker ON theses(ticker);
CREATE INDEX idx_catalysts_ticker ON catalysts(ticker);
CREATE INDEX idx_catalysts_date ON catalysts(expected_date);
CREATE INDEX idx_deep_dives_ticker ON deep_dives(ticker);
CREATE INDEX idx_macro_snapshots_date ON macro_snapshots(date);
CREATE INDEX idx_portfolio_snapshots_date ON portfolio_snapshots(date);

-- ============================================================
-- RLS — habilitar em todas as tabelas
-- Policy permissiva (app de usuário único, auth no Streamlit)
-- ============================================================
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE theses ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalysts ENABLE ROW LEVEL SECURITY;
ALTER TABLE macro_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE deep_dives ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all for anon" ON positions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON transactions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON theses FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON catalysts FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON macro_snapshots FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON deep_dives FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON analysis_reports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON portfolio_snapshots FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- Trigger para updated_at automático
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON theses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
