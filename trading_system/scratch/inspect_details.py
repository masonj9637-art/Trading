import pandas as pd

df_yes = pd.read_csv('/home/mason/Trading/scratch/yes_group_all_valid.csv')
df_no = pd.read_csv('/home/mason/Trading/scratch/no_group_all_valid.csv')

print("=== YES GROUP INDIVIDUAL FILINGS ===")
print(df_yes[['ticker', 'industry', 'filing_date', 'p_m1', 'p_p15', 'vol_ratio', 'pct_1d', 'pct_5d', 'pct_15d', 'abs_15d', 'classification', 'flagged']].to_string())

print("\n=== NO GROUP FLAGGED FILINGS ===")
print(df_no[df_no['flagged']][['ticker', 'industry', 'filing_date', 'p_m1', 'p_p15', 'vol_ratio', 'pct_15d', 'abs_15d', 'classification']].to_string())

print("\n=== MINING NO GROUP OUTLIERS (Why abs_15d is high) ===")
print(df_no[df_no['industry']=='Mining'].sort_values('abs_15d', ascending=False)[['ticker', 'filing_date', 'p_m1', 'p_p15', 'pct_15d', 'abs_15d']].head(10).to_string())
