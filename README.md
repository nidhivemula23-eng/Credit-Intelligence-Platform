# Credit Intelligence Platform

**Financial Health \& Credit Risk Assessment of Indian Listed Companies (FY2021–FY2025)**

A self-built, end-to-end credit rating system modelled on how agencies like CRISIL and ICRA assess corporate credit risk, covering 20 NSE/BSE-listed companies across four sectors. Built from scratch, including learning SQL and Power BI during the project itself.

*Not affiliated with CRISIL, ICRA, or any rating agency. Built for portfolio and learning purposes; see the report's Disclaimer section for full details.*



## What This Project Does

Takes raw financial statements (Income Statement, Balance Sheet, Cash Flow) for 20 companies over 5 years, and turns them into:

* 10 calculated financial ratios per company-year (Liquidity, Leverage, Profitability, Cash Flow, Efficiency)
* A weighted 0-100 credit score per company-year
* A letter rating (AAA down to C/D)
* An interactive Power BI dashboard
* A full analyst-style written report, including 3 in-depth company deep-dives

## Coverage

|Sector|Companies|
|-|-|
|Auto|Ashok Leyland, Maruti Suzuki, Mahindra \& Mahindra, Bajaj Auto, Hero MotoCorp|
|Steel|Tata Steel, JSW Steel, Steel Authority of India, Jindal Steel \& Power, APL Apollo Tubes|
|FMCG|Hindustan Unilever, ITC, Colgate-Palmolive (India), Britannia, Dabur|
|Telecom|Bharti Airtel, Vodafone Idea, Tata Communications, Indus Towers, MTNL|

*(Two companies: Tata Motors and Nestlé India were substituted mid-project due to a corporate demerger and a fiscal-year change respectively, both disrupting clean year-over-year comparison. Full reasoning in the report's Methodology section.)*

## 

## Tech Stack

|Tool|Purpose|
|-|-|
|PostgreSQL|Relational database- Companies, Income Statement, Balance Sheet, Cash Flow, and Ratios tables|
|Python|Data loading, ratio calculation, credit scoring engine, chart generation|
|Power BI|Interactive dashboard- explore any company or sector live|
|Microsoft Word|Final analyst-style report|

## 

## Methodology Summary

Each company-year is scored across 5 weighted categories:

|Category|Weight|Ratios|
|-|-|-|
|Liquidity|25 pts|Current Ratio, Quick Ratio|
|Leverage|25 pts|Debt/Equity, Debt/EBITDA, Interest Coverage|
|Profitability|20 pts|ROE, ROCE, EBITDA Margin|
|Cash Flow|20 pts|CFO Margin|
|Efficiency|10 pts|Asset Turnover|

Full scoring thresholds, ratio definitions, and methodology notes (including how negative-equity companies are handled) are documented in the report.

## Key Findings

* **FMCG was the strongest sector every single year** (avg. FY2025 score: 84.9): low debt, stable margins, structurally different risk profile from every other sector studied.
* **Steel showed the sharpest single-year swing** in the dataset: a 17-point average score drop in FY2023, driven by a real, documented industry-wide input-cost and export-duty shock.
* **Revenue growth alone isn't a reliable credit signal**: one company in this study grew revenue every year for four years while its credit rating still declined, because leverage and core profitability moved the opposite way.
* **Cash flow and accounting profit can tell opposite stories** : two companies in the Telecom sector show strongly positive operating cash flow *despite* large reported net losses, a pattern explained by heavy non-cash depreciation rather than genuine unprofitability.

## Data Sources

* Primary: [screener.in](https://www.screener.in)
* Secondary/cross-check: moneycontrol.com, company annual reports

## Author

Nidhi Bhagwandas Vemula

