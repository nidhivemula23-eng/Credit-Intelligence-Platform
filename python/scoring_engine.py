"""
scoring_engine.py reads calculated ratios from the Ratios table, scores
each company 0-100 using weighted, tiered thresholds, assigns a
CRISIL-style letter rating, and writes both back into the Ratios table.
"""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "credit_intel",
    "user": "postgres",
    "password": "YOUR PASSWROD HERE",
}


def score_band(value, bands, max_points):
    """
    Generic scorer: given a value and a list of (threshold, fraction)
    tuples ordered from BEST to WORST, returns points earned out of
    max_points. NULL/None values (Not Meaningful ratios) always score 0 
    """
    if value is None:
        return 0.0
    for cutoff, fraction, direction in bands:
        if direction == "higher_is_better" and value >= cutoff:
            return round(max_points * fraction, 2)
        if direction == "lower_is_better" and value <= cutoff:
            return round(max_points * fraction, 2)
    return 0.0  # fell through every band = worst tier


def calculate_score(ratios):
    (current_ratio, quick_ratio, roe, roce, ebitda_margin,
     interest_coverage, debt_equity, debt_ebitda, cfo_margin,
     asset_turnover) = ratios

    scores = {}

    # LIQUIDITY (25 pts: 12.5 + 12.5)
    scores["current_ratio"] = score_band(current_ratio, [
        (1.5, 1.00, "higher_is_better"),
        (1.2, 0.80, "higher_is_better"),
        (1.0, 0.60, "higher_is_better"),
        (0.8, 0.40, "higher_is_better"),
    ], 12.5)

    scores["quick_ratio"] = score_band(quick_ratio, [
        (1.2, 1.00, "higher_is_better"),
        (0.8, 0.80, "higher_is_better"),
        (0.6, 0.50, "higher_is_better"),
        (0.4, 0.25, "higher_is_better"),
    ], 12.5)

    # LEVERAGE (25 pts: ~8.33 each) 
    scores["debt_equity"] = score_band(debt_equity, [
        (0.5, 1.00, "lower_is_better"),
        (1.0, 0.80, "lower_is_better"),
        (2.0, 0.50, "lower_is_better"),
        (3.0, 0.25, "lower_is_better"),
    ], 8.33)

    scores["debt_ebitda"] = score_band(debt_ebitda, [
        (1.0, 1.00, "lower_is_better"),
        (3.0, 0.80, "lower_is_better"),
        (5.0, 0.50, "lower_is_better"),
        (7.0, 0.25, "lower_is_better"),
    ], 8.33)

    scores["interest_coverage"] = score_band(interest_coverage, [
        (8.0, 1.00, "higher_is_better"),
        (4.0, 0.80, "higher_is_better"),
        (2.0, 0.50, "higher_is_better"),
        (1.0, 0.25, "higher_is_better"),
    ], 8.34)  # 8.33+8.33+8.34 = 25.00 exactly

    # PROFITABILITY (20 pts: 6.67 each) 
    scores["roe"] = score_band(roe, [
        (20, 1.00, "higher_is_better"),
        (15, 0.80, "higher_is_better"),
        (10, 0.60, "higher_is_better"),
        (5, 0.40, "higher_is_better"),
    ], 6.67)

    scores["roce"] = score_band(roce, [
        (20, 1.00, "higher_is_better"),
        (15, 0.80, "higher_is_better"),
        (10, 0.60, "higher_is_better"),
        (5, 0.40, "higher_is_better"),
    ], 6.67)

    scores["ebitda_margin"] = score_band(ebitda_margin, [
        (20, 1.00, "higher_is_better"),
        (15, 0.80, "higher_is_better"),
        (10, 0.60, "higher_is_better"),
        (5, 0.40, "higher_is_better"),
    ], 6.66)  # 6.67+6.67+6.66 = 20.00 exactly

    #  CASH FLOW (20 pts, all on CFO margin) 
    scores["cfo_margin"] = score_band(cfo_margin, [
        (15, 1.00, "higher_is_better"),
        (10, 0.80, "higher_is_better"),
        (5, 0.60, "higher_is_better"),
        (0, 0.40, "higher_is_better"),
    ], 20.0)

    #EFFICIENCY (10 pts, all on Asset Turnover) 
    scores["asset_turnover"] = score_band(asset_turnover, [
        (1.5, 1.00, "higher_is_better"),
        (1.0, 0.80, "higher_is_better"),
        (0.7, 0.60, "higher_is_better"),
        (0.4, 0.40, "higher_is_better"),
    ], 10.0)

    total = round(sum(scores.values()), 2)
    return total, scores


def score_to_rating(score):
    if score >= 90:
        return "AAA"
    elif score >= 80:
        return "AA"
    elif score >= 70:
        return "A"
    elif score >= 60:
        return "BBB"
    elif score >= 50:
        return "BB"
    elif score >= 40:
        return "B"
    else:
        return "C/D"


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT c.company_name, r.company_id, r.fiscal_year,
               r.current_ratio, r.quick_ratio, r.roe, r.roce,
               r.ebitda_margin, r.interest_coverage, r.debt_equity,
               r.debt_ebitda, r.cfo_margin, r.asset_turnover
        FROM Ratios r
        JOIN Companies c ON c.company_id = r.company_id
        ORDER BY c.company_name, r.fiscal_year;
    """)
    rows = cur.fetchall()
    print(f"Scoring {len(rows)} company-year rows...\n")

    for row in rows:
        (company_name, company_id, fiscal_year, *ratio_values) = row
        total_score, breakdown = calculate_score(ratio_values)
        rating = score_to_rating(total_score)

        cur.execute("""
            UPDATE Ratios
            SET credit_score = %s, credit_rating = %s
            WHERE company_id = %s AND fiscal_year = %s;
        """, (total_score, rating, company_id, fiscal_year))

        print(f"  {company_name:28s} FY{fiscal_year}  Score: {total_score:6.2f}  Rating: {rating}")

    conn.commit()
    cur.close()
    conn.close()
    print("\nDone. Scores and ratings written to Ratios table.")


if __name__ == "__main__":
    main()
