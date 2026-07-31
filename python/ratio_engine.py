"""
ratio_engine.py reads raw financial data from your PostgreSQL database,
calculates all 10 credit ratios, and writes the results into the Ratios
table.

WHAT THIS SCRIPT DOES:
- Pulls every company-year row by JOINing Income_Statement, Balance_Sheet,
  and Cash_Flow together (same JOIN pattern you've already run in pgAdmin)
- For each row, calculates all 10 ratios using the raw numbers
- Handles "not meaningful" cases explicitly instead of computing a
  misleading number (see NEGATIVE EQUITY note below)
- Writes everything into the Ratios table, one row per company-year
"""

import psycopg2


# DATABASE CONNECTION

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "credit_intel",
    "user": "postgres",
    "password": "YOUR PASSWORD HERE",
}


def safe_div(numerator, denominator, multiplier=1):
    """
    Divides two numbers, but returns None (SQL NULL) instead of crashing
    if the denominator is missing or zero. 'multiplier' lets us convert
    to a percentage (multiplier=100) where needed.
    """
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round((numerator / denominator) * multiplier, 2)


def safe_div_equity_sensitive(numerator, equity, multiplier=1):
    """
    Same as safe_div, but specifically for ratios that divide by EQUITY
    (ROE, Debt/Equity). If equity is negative or zero, the company has
    already burned through its capital base, dividing by a negative
    number here would flip the sign and produce a number that LOOKS
    fine but means the opposite of what it appears to say. Real analysts
    call this "Not Meaningful" (NM) rather than report it. We return
    None here, which becomes NULL in SQL and "NM" when you display it
    later in your report/dashboard.
    """
    if numerator is None or equity is None or equity <= 0:
        return None
    return round((numerator / equity) * multiplier, 2)


def calculate_ratios(row):
    (company_id, fiscal_year,
     revenue, ebitda, ebit, interest_expense, net_profit,
     total_assets, total_equity, total_debt,
     current_assets, current_liabilities, inventory,
     cfo) = row

    capital_employed = None
    if total_assets is not None and current_liabilities is not None:
        capital_employed = total_assets - current_liabilities

    ratios = {
        "current_ratio": safe_div(current_assets, current_liabilities),
        "quick_ratio": safe_div(
            (current_assets - inventory) if current_assets is not None and inventory is not None else None,
            current_liabilities,
        ),
        "roe": safe_div_equity_sensitive(net_profit, total_equity, multiplier=100),
        "roce": safe_div(ebit, capital_employed, multiplier=100),
        "ebitda_margin": safe_div(ebitda, revenue, multiplier=100),
        "interest_coverage": safe_div(ebit, interest_expense),
        "debt_equity": safe_div_equity_sensitive(total_debt, total_equity),
        "debt_ebitda": safe_div(total_debt, ebitda),
        "cfo_margin": safe_div(cfo, revenue, multiplier=100),
        "asset_turnover": safe_div(revenue, total_assets),
    }
    return company_id, fiscal_year, ratios


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT c.company_id, i.fiscal_year,
               i.revenue, i.ebitda, i.ebit, i.interest_expense, i.net_profit,
               b.total_assets, b.total_equity, b.total_debt,
               b.current_assets, b.current_liabilities, b.inventory,
               cf.cfo
        FROM Companies c
        JOIN Income_Statement i ON c.company_id = i.company_id
        JOIN Balance_Sheet b ON c.company_id = b.company_id AND i.fiscal_year = b.fiscal_year
        JOIN Cash_Flow cf ON c.company_id = cf.company_id AND i.fiscal_year = cf.fiscal_year
        ORDER BY c.company_id, i.fiscal_year;
    """)
    rows = cur.fetchall()
    print(f"Fetched {len(rows)} company-year rows.\n")

    nm_count = 0
    for row in rows:
        company_id, fiscal_year, ratios = calculate_ratios(row)

        if ratios["roe"] is None or ratios["debt_equity"] is None:
            nm_count += 1

        columns = ["company_id", "fiscal_year"] + list(ratios.keys())
        values = [company_id, fiscal_year] + list(ratios.values())
        placeholders = ", ".join(["%s"] * len(values))
        col_names = ", ".join(columns)
        update_clause = ", ".join(
            f"{col} = EXCLUDED.{col}" for col in ratios.keys()
        )

        sql = f"""
            INSERT INTO Ratios ({col_names})
            VALUES ({placeholders})
            ON CONFLICT (company_id, fiscal_year)
            DO UPDATE SET {update_clause};
        """
        cur.execute(sql, values)

    conn.commit()
    cur.close()
    conn.close()

    print(f"Done. {len(rows)} rows of ratios calculated and saved.")
    print(f"{nm_count} row(s) had ROE or Debt/Equity marked 'Not Meaningful' "
          f"due to negative equity (expected for your distressed companies).")


if __name__ == "__main__":
    main()
