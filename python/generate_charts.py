"""
generate_charts.py pulls data from your PostgreSQL database and
auto-generates PNG charts for your report: one score-trend + one
revenue-trend chart per company, one peer-comparison bar chart per
sector, and one sector-average trend chart.
"""

import os
import psycopg2
import matplotlib
matplotlib.use("Agg")  # renders to file without needing a display window
import matplotlib.pyplot as plt

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "credit_intel",
    "user": "postgres",
    "password": "YOUR PASSWORD HERE",
}

OUTPUT_DIR = "charts"


def slugify(name):
    """Turns 'Colgate-Palmolive (India)' into 'colgate_palmolive_india' for filenames."""
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def fetch_data(cur):
    cur.execute("""
        SELECT c.company_id, c.company_name, c.sector, i.fiscal_year,
               i.revenue, r.credit_score, r.credit_rating
        FROM Companies c
        JOIN Income_Statement i ON c.company_id = i.company_id
        JOIN Ratios r ON c.company_id = r.company_id AND i.fiscal_year = r.fiscal_year
        ORDER BY c.company_name, i.fiscal_year;
    """)
    rows = cur.fetchall()

    # Organize into a dict keyed by company name for easy per-company plotting
    companies = {}
    for company_id, name, sector, year, revenue, score, rating in rows:
        if name not in companies:
            companies[name] = {"sector": sector, "years": [], "revenue": [],
                                "score": [], "rating": []}
        companies[name]["years"].append(year)
        companies[name]["revenue"].append(revenue)
        companies[name]["score"].append(score)
        companies[name]["rating"].append(rating)
    return companies


def plot_company_charts(companies):
    for name, data in companies.items():
        slug = slugify(name)

        #Credit score trend
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(data["years"], data["score"], marker="o", linewidth=2, color="#1F4E78")
        ax.set_title(f"{name} - Credit Score Trend (FY21-FY25)")
        ax.set_xlabel("Fiscal Year")
        ax.set_ylabel("Credit Score (0-100)")
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3)
        for x, y, rating in zip(data["years"], data["score"], data["rating"]):
            ax.annotate(rating, (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
        fig.tight_layout()
        fig.savefig(f"{OUTPUT_DIR}/{slug}_score_trend.png", dpi=150)
        plt.close(fig)

        #Revenue trend
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(data["years"], data["revenue"], marker="o", linewidth=2, color="#2E7D32")
        ax.set_title(f"{name} — Revenue Trend (FY21-FY25)")
        ax.set_xlabel("Fiscal Year")
        ax.set_ylabel("Revenue (INR Crores)")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(f"{OUTPUT_DIR}/{slug}_revenue_trend.png", dpi=150)
        plt.close(fig)


def plot_sector_peer_comparison(companies, latest_year=2025):
    sectors = {}
    for name, data in companies.items():
        sector = data["sector"]
        if latest_year in data["years"]:
            idx = data["years"].index(latest_year)
            sectors.setdefault(sector, []).append((name, data["score"][idx]))

    for sector, entries in sectors.items():
        entries.sort(key=lambda x: x[1], reverse=True)
        names = [e[0] for e in entries]
        scores = [e[1] for e in entries]

        fig, ax = plt.subplots(figsize=(7, 4))
        colors = ["#1F4E78" if s >= 70 else "#C77800" if s >= 50 else "#B00020" for s in scores]
        ax.bar(names, scores, color=colors)
        ax.set_title(f"{sector} Sector - Credit Score Comparison (FY{latest_year})")
        ax.set_ylabel("Credit Score (0-100)")
        ax.set_ylim(0, 100)
        plt.xticks(rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(f"{OUTPUT_DIR}/sector_{slugify(sector)}_peer_comparison.png", dpi=150)
        plt.close(fig)


def plot_sector_average_trend(companies):
    sector_year_scores = {}
    for name, data in companies.items():
        sector = data["sector"]
        for year, score in zip(data["years"], data["score"]):
            sector_year_scores.setdefault(sector, {}).setdefault(year, []).append(score)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for sector, year_scores in sector_year_scores.items():
        years = sorted(year_scores.keys())
        avg_scores = [sum(year_scores[y]) / len(year_scores[y]) for y in years]
        ax.plot(years, avg_scores, marker="o", linewidth=2, label=sector)

    ax.set_title("Sector Average Credit Score Trend (FY21-FY25)")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Average Credit Score")
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/sector_average_trend.png", dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    companies = fetch_data(cur)
    print(f"Fetched data for {len(companies)} companies.")

    plot_company_charts(companies)
    print(f"Saved {len(companies) * 2} per-company charts (score + revenue trend).")

    plot_sector_peer_comparison(companies)
    print("Saved peer comparison charts (1 per sector).")

    plot_sector_average_trend(companies)
    print("Saved sector average trend chart.")

    cur.close()
    conn.close()
    print(f"\nDone. All charts saved in the '{OUTPUT_DIR}' folder.")


if __name__ == "__main__":
    main()
