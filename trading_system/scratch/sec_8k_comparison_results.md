# SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)

## Executive Summary

This report evaluates the predictive value of LLM content-based filtering of SEC Form 8-K disclosures across three small-cap industry groups ($50M – $500M market cap) during the window of **July 23, 2025 – July 23, 2026**:
1. **Small-Cap Mining & Exploration** ([mining_8k_review.md](file:///home/mason/Trading/scratch/mining_8k_review.md))
2. **Small-Cap Specialty Finance & Fintech** ([fintech_8k_review.md](file:///home/mason/Trading/scratch/fintech_8k_review.md))
3. **Small-Cap Biotech & Pharma** ([biotech_8k_review.md](file:///home/mason/Trading/scratch/biotech_8k_review.md))

The target test compares all filings marked **"Yes"** (LLM-predicted plausible price movers) against an equal-sized random sample of filings marked **"No"** (routine disclosures) matched by industry, timeframe, and count.

Using historical daily stock bars from Alpaca (`TimeFrame.Day`, `DataFeed.IEX`), price and volume reaction data ($t-10$ to $t+15$ relative to filing date $t_0$) were computed to determine classification (`INSTANT`, `GRADUAL`, `FLAT/NONE`), volume ratio (post-filing 15d average volume vs. pre-filing 10d average volume), and the **Flagged** criteria (`vol_ratio > 2.0x` AND `classification == GRADUAL`).

---

## 1. Dataset & Bar Window Coverage Summary

| Industry Sector | Total Reviewed Filings | Marked "Yes" (LLM Flagged) | Marked "No" (Routine Disclosure) | Valid 15-Day Windows ("Yes") | Valid 15-Day Windows ("No Pool") |
|---|---|---|---|---|---|
| **Small-Cap Mining** | 74 | 10 | 64 | 6 | 33 |
| **Fintech / Specialty Finance** | 70 | 14 | 56 | 9 | 41 |
| **Biotech & Pharma** | 72 | 6 | 66 | 4 | 49 |
| **TOTAL** | **216** | **30** | **186** | **19** | **123** |

*Note: 11 "Yes" filings and 63 "No" filings either occurred within the 15 trading days prior to July 24, 2026 (incomplete post-filing evaluation window) or were OTC tickers without trading bar data on Alpaca IEX.*

---

## 2. Direct Comparison Results

A **100-seed Monte Carlo matched random sampling** was conducted for the "No" control group (matching 6 Mining, 9 Fintech, 4 Biotech; $N=19$), alongside an evaluation of the **entire valid "No" pool ($N=123$)**.

| Performance Metric | "Yes" Group (Agent Selected, $N=19$) | "No" Group (100-Seed Monte Carlo Matched, $N=19$) | "No" Group (Full Universe Pool, $N=123$) |
|---|---|---|---|
| **% FLAGGED (`>2x Vol` & `GRADUAL`)** | **10.5%** (2/19) | **7.3% (±5.7%)** | **8.1%** (10/123) |
| **% Volume Spike (`>2x Vol`)** | **21.1%** (4/19) | **16.5% (±7.3%)** | **15.4%** (19/123) |
| **Mean Volume Ratio (Post/Pre)** | **1.56x** | **1.53x** | **1.48x** |
| **Median Volume Ratio** | **1.50x** | — | **1.16x** |
| **Mean Abs 1-Day Price Move** | **7.27%** | **5.17%** | **5.91%** |
| **Median Abs 1-Day Price Move** | **4.35%** | — | **3.36%** |
| **Mean Abs 5-Day Price Move** | **11.95%** | **14.77%** | **15.01%** |
| **Median Abs 5-Day Price Move** | **8.89%** | — | **5.85%** |
| **Mean Abs 15-Day Price Move** | **11.84%** | **18.57%** | **18.98%** |
| **Median Abs 15-Day Price Move** | **10.87%** | — | **7.96%** |
| **Mean Directional 1-Day Return** | **+1.14%** | **-0.64%** | **-0.84%** |
| **Mean Directional 5-Day Return** | **+4.55%** | **+7.59%** | **+6.40%** |
| **Mean Directional 15-Day Return** | **+2.72%** | **+8.11%** | **+7.68%** |
| **% Classified GRADUAL** | **47.4%** (9/19) | **56.1%** | **59.3%** (73/123) |
| **% Classified INSTANT** | **21.1%** (4/19) | **8.6%** | **10.6%** (13/123) |
| **% Classified FLAT/NONE** | **31.6%** (6/19) | **35.4%** | **30.1%** (37/123) |

---

## 3. Industry-Level Breakdown

| Industry Sector | Group | Valid N | % Flagged | % Vol > 2x | Avg Vol Ratio | Avg Abs 1d Move | Avg Abs 5d Move | Avg Abs 15d Move |
|---|---|---|---|---|---|---|---|---|
| **Mining** | **Yes** | 6 | 16.7% | 16.7% | 1.46x | 5.80% | 11.64% | 12.94% |
| | **No** | 33 | 3.0% | 6.1% | 1.09x | 7.75% | 35.40% | 39.51%* |
| **Fintech** | **Yes** | 9 | 11.1% | 33.3% | 1.75x | 7.12% | 12.05% | 13.90% |
| | **No** | 41 | 7.3% | 22.0% | 1.76x | 2.49% | 5.13% | 8.41% |
| **Biotech** | **Yes** | 4 | 0.0% | 0.0% | 1.29x | 9.84% | 12.21% | 5.54% |
| | **No** | 49 | 12.2% | 16.3% | 1.52x | 7.53% | 9.55% | 14.00% |

*\*Note: The Mining "No" group mean 15-day move was distorted by micro-cap penny stock SOWG (+969.9% price move).*

---

## 4. Key Findings & Strategic Conclusion

1. **Flagged Rate (`>2x Volume` & `GRADUAL`)**:
   - The "Yes" group produced a **10.5%** flag rate vs. **7.3% (±5.7%)** for the matched random "No" control sample (and **8.1%** across the full 123-filing "No" pool).
   - The $+2.4\%$ variance above random sampling is statistically insignificant and well within the 1-standard-deviation error margin ($\pm 5.7\%$).

2. **Price Movement**:
   - **Immediate Volatility (Day 1)**: The "Yes" group exhibited slightly higher day-1 move magnitude (**7.27%** mean / **4.35%** median vs. **5.17%** mean / **3.36%** median for "No").
   - **15-Day Move**: Median 15-day absolute price move was **10.87%** ("Yes") vs. **7.96%** ("No").

3. **Core Conclusion**:
   - The LLM agents' content-based screening (reading SEC 8-K disclosures and tagging predicted movers as "Yes") **does not provide a statistically meaningful edge** over random selection on volume flagging or sustained price drift.
   - Qualitative text evaluation of routine 8-K filings must be paired with real-time price/volume reaction triggers rather than relying solely on pre-market content analysis.
