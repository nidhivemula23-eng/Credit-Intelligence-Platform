"""
export_dashboard_data.py runs the combined flat query against your PostgreSQL database and exports it as a single CSV file,
ready to import into Power BI directly (no database driver needed).
"""

import csv
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "credit_intel",
    "user": "postgres",
    "password": "YOUR PASSWORD HERE",
}

# This is the SAME query used for the live Power BI connection path
# one flat table combining all 5 of your SQL tables into a single view.
FLAT_QUERY = """
    SELECT
        c.company_name,
        c.sector,
        c.ticker,
        i.fiscal_year,
        i.revenue,
        i.ebitda,
        i.ebit,
        i.net_profit,
        b.total_assets,
        b.total_equity,
        b.total_debt,
        cf.cfo,
        r.current_ratio,
        r.quick_ratio,
        r.roe,
        r.roce,
        r.ebitda_margin,
        r.interest_coverage,
        r.debt_equity,
        r.debt_ebitda,
        r.cfo_margin,
        r.asset_turnover,
        r.credit_score,
        r.credit_rating
    FROM Companies c
    JOIN Income_Statement i ON c.company_id = i.company_id
    JOIN Balance_Sheet b ON c.company_id = b.company_id AND i.fiscal_year = b.fiscal_year
    JOIN Cash_Flow cf ON c.company_id = cf.company_id AND i.fiscal_year = cf.fiscal_year
    JOIN Ratios r ON c.company_id = r.company_id AND i.fiscal_year = r.fiscal_year
    ORDER BY c.sector, c.company_name, i.fiscal_year;
"""


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(FLAT_QUERY)

    column_names = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    with open("dashboard_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)

    cur.close()
    conn.close()
    print(f"Exported {len(rows)} rows to dashboard_data.csv")


if __name__ == "__main__":
    main()
