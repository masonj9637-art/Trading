# Filtered SEC Filings Subset

## Summary
- **Original Filings in Dataset**: 50 total (45 fully analyzed, 5 insufficient data)
- **Surviving Filings**: **9** rows out of 45 analyzed (**20.0%** survival rate)
- **Excluded Filings**: 36 rows failed one or more criteria

---

## Filtering Funnel & Breakdown

| Filtering Criterion | Description | Rows Passing (out of 45 analyzed) |
|---|---|---|
| **Criterion 1: Material Item Type** | Must disclose Item 1.01, 2.01, 4.02, 3.01, 5.02, or 2.02 (excludes routine 7.01/8.01/9.01/5.07/4.01) | 16 rows |
| **Criterion 2: Liquidity Threshold** | Average daily volume $\ge 5,000$ shares in either pre- or post-filing window | 33 rows |
| **Criterion 3: Filing Frequency** | Excludes tickers appearing $>3$ times in the 50-row dataset (`MBOT`, `HURC`, `SERV`, `PDYN`) | 14 rows |
| **ALL THREE CRITERIA** | **Intersection of C1, C2, and C3** | **9 rows** |

---

## Filtered Market Data Price & Volume Reactions

> Sorted by **Classification** (`GRADUAL` first) then by **Volume Ratio** descending.

| Ticker | Filing Date | Filing Type | Disclosed Item Types | Price 1 day before | Price on filing date | Price 1 day after | Price 5 days after | Price 15 days after | Average daily volume (10 days before) | Average daily volume (15 days after) | Volume ratio (after/before) | Classification | Flagged |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CLPT | 2026-05-13 | 8-K | Item 2.02, Item 7.01, Item 9.01 | $12.630 | $12.180 | $12.780 | $11.180 | $14.355 | 16,467 | 20,538 | 1.25x | GRADUAL | No |
| CLPT | 2026-05-21 | 8-K | Item 5.02, Item 5.07, Item 9.01 | $11.180 | $11.715 | $11.440 | $12.700 | $13.490 | 18,796 | 19,369 | 1.03x | GRADUAL | No |
| RR | 2026-06-12 | 8-K | Item 4.02, Item 9.01 | $2.300 | $2.125 | $2.135 | $2.145 | $1.825 | 288,109 | 284,563 | 0.99x | GRADUAL | No |
| XTIA | 2026-04-15 | 8-K | Item 2.02, Item 9.01 | $2.090 | $2.330 | $2.520 | $2.120 | $1.850 | 35,936 | 32,633 | 0.91x | GRADUAL | No |
| CMCO | 2026-04-13 | 8-K | Item 5.02, Item 7.01, Item 9.01 | $15.690 | $15.950 | $16.105 | $16.020 | $14.760 | 19,941 | 12,576 | 0.63x | GRADUAL | No |
| RR | 2026-05-28 | 8-K | Item 3.01, Item 8.01, Item 9.01 | $3.270 | $3.245 | $3.020 | $2.725 | $2.135 | 519,574 | 277,621 | 0.53x | GRADUAL | No |
| RR | 2026-06-03 | 8-K | Item 2.01, Item 8.01, Item 9.01 | $2.980 | $2.695 | $2.725 | $2.190 | $1.905 | 518,086 | 258,873 | 0.50x | GRADUAL | No |
| XTIA | 2026-05-14 | 8-K | Item 2.02, Item 9.01 | $1.860 | $1.800 | $1.795 | $1.730 | $1.825 | 25,806 | 62,467 | 2.42x | FLAT/NONE | No |
| CMCO | 2026-06-25 | 8-K | Item 2.02, Item 7.01, Item 9.01 | $13.960 | $14.815 | $14.460 | $13.540 | $14.350 | 43,875 | 28,573 | 0.65x | FLAT/NONE | No |
