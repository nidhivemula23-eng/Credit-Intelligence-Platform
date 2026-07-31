
-- CREDIT INTELLIGENCE PLATFORM - DATABASE SCHEMA



-- TABLE 1: COMPANIES (the "master" table- every other table
-- points back to this one)


CREATE TABLE Companies (
    company_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(100) NOT NULL,
    ticker          VARCHAR(20)  NOT NULL,
    sector          VARCHAR(50)  NOT NULL,
    listing_year    INT
);


-- TABLE 2: INCOME_STATEMENT (one row per company per year)

CREATE TABLE Income_Statement (
    id                  SERIAL PRIMARY KEY,
    company_id          INT REFERENCES Companies(company_id),
    fiscal_year         INT NOT NULL,
    revenue             NUMERIC(15,2),
    ebitda              NUMERIC(15,2),
    ebit                NUMERIC(15,2),
    interest_expense    NUMERIC(15,2),
    depreciation        NUMERIC(15,2),
    tax                 NUMERIC(15,2),
    net_profit          NUMERIC(15,2),

    -- SQL CONCEPT: UNIQUE constraint across multiple columns.
    -- This stops you from accidentally loading the same
    -- company + year combination twice.
    UNIQUE(company_id, fiscal_year)
);


-- TABLE 3: BALANCE_SHEET

CREATE TABLE Balance_Sheet (
    id                      SERIAL PRIMARY KEY,
    company_id              INT REFERENCES Companies(company_id),
    fiscal_year             INT NOT NULL,
    total_assets            NUMERIC(15,2),
    total_equity            NUMERIC(15,2),
    total_debt              NUMERIC(15,2),
    current_assets          NUMERIC(15,2),
    current_liabilities     NUMERIC(15,2),
    inventory               NUMERIC(15,2),
    cash_and_equivalents    NUMERIC(15,2),
    UNIQUE(company_id, fiscal_year)
);


-- TABLE 4: CASH_FLOW
CREATE TABLE Cash_Flow (
    id              SERIAL PRIMARY KEY,
    company_id      INT REFERENCES Companies(company_id),
    fiscal_year     INT NOT NULL,
    cfo             NUMERIC(15,2),   -- cash flow from operations
    cfi             NUMERIC(15,2),   -- cash flow from investing
    cff             NUMERIC(15,2),   -- cash flow from financing
    capex           NUMERIC(15,2),
    UNIQUE(company_id, fiscal_year)
);



-- TABLE 5: RATIOS 
CREATE TABLE Ratios (
    id                  SERIAL PRIMARY KEY,
    company_id          INT REFERENCES Companies(company_id),
    fiscal_year         INT NOT NULL,
    current_ratio       NUMERIC(10,2),
    quick_ratio         NUMERIC(10,2),
    roe                 NUMERIC(10,2),
    roce                NUMERIC(10,2),
    ebitda_margin       NUMERIC(10,2),
    interest_coverage   NUMERIC(10,2),
    debt_equity         NUMERIC(10,2),
    debt_ebitda         NUMERIC(10,2),
    cfo_margin          NUMERIC(10,2),
    asset_turnover      NUMERIC(10,2),
    credit_score        NUMERIC(5,2),
    credit_rating       VARCHAR(5),
    UNIQUE(company_id, fiscal_year)
);


-- SEED DATA: your 20 companies


INSERT INTO Companies (company_name, ticker, sector, listing_year) VALUES
('Ashok Leyland',          'ASHOKLEY',   'Auto',     1948),
('Maruti Suzuki India',    'MARUTI',     'Auto',     2003),
('Mahindra & Mahindra',    'M&M',        'Auto',     1956),
('Bajaj Auto',             'BAJAJ-AUTO', 'Auto',     2008),
('Hero MotoCorp',          'HEROMOTOCO', 'Auto',     2003),

('Tata Steel',             'TATASTEEL',  'Steel',    1907),
('JSW Steel',              'JSWSTEEL',   'Steel',    1994),
('Steel Authority of India','SAIL',      'Steel',    1974),
('Jindal Steel & Power',   'JINDALSTEL', 'Steel',    2003),
('APL Apollo Tubes',       'APLAPOLLO',  'Steel',    1993),

('Hindustan Unilever',     'HINDUNILVR', 'FMCG',     1956),
('ITC',                    'ITC',        'FMCG',     1970),
('Nestle India',           'NESTLEIND',  'FMCG',     1969),
('Britannia Industries',   'BRITANNIA',  'FMCG',     1918),
('Dabur India',            'DABUR',      'FMCG',     1994),

('Bharti Airtel',          'BHARTIARTL', 'Telecom',  2002),
('Vodafone Idea',          'IDEA',       'Telecom',  2007),
('Tata Communications',    'TATACOMM',   'Telecom',  1986),
('Indus Towers',           'INDUSTOWER', 'Telecom',  2013),
('MTNL',                   'MTNL',       'Telecom',  2001);


SELECT * FROM Companies ORDER BY sector, company_name;
