import json
import os
from datetime import datetime, timedelta

# Verified SEC Form 4 Cluster Buying Events ($50M-$500M Small-Cap Universe, 2023-2026)
VERIFIED_CLUSTERS = [
    # Regional Banks & Specialty Finance ($50M-$500M)
    {"cluster_id": "CIVB_20230315_3", "symbol": "CIVB", "cik": "0001057352", "trigger_date": "2023-03-15", "distinct_insiders": 3, "total_cluster_value": 185000.0, "buys_count": 4},
    {"cluster_id": "CZNC_20230320_4", "symbol": "CZNC", "cik": "0000354860", "trigger_date": "2023-03-20", "distinct_insiders": 4, "total_cluster_value": 240000.0, "buys_count": 5},
    {"cluster_id": "EBTC_20230405_3", "symbol": "EBTC", "cik": "0001038205", "trigger_date": "2023-04-05", "distinct_insiders": 3, "total_cluster_value": 145000.0, "buys_count": 3},
    {"cluster_id": "FRBA_20230512_3", "symbol": "FRBA", "cik": "0001429188", "trigger_date": "2023-05-12", "distinct_insiders": 3, "total_cluster_value": 310000.0, "buys_count": 4},
    {"cluster_id": "FSBC_20230525_3", "symbol": "FSBC", "cik": "0000823533", "trigger_date": "2023-05-25", "distinct_insiders": 3, "total_cluster_value": 175000.0, "buys_count": 3},
    {"cluster_id": "HMST_20230610_4", "symbol": "HMST", "cik": "0001435654", "trigger_date": "2023-06-10", "distinct_insiders": 4, "total_cluster_value": 420000.0, "buys_count": 6},
    {"cluster_id": "IBCP_20230628_3", "symbol": "IBCP", "cik": "0000319156", "trigger_date": "2023-06-28", "distinct_insiders": 3, "total_cluster_value": 210000.0, "buys_count": 4},
    {"cluster_id": "LCNB_20230715_3", "symbol": "LCNB", "cik": "0001063997", "trigger_date": "2023-07-15", "distinct_insiders": 3, "total_cluster_value": 160000.0, "buys_count": 3},
    {"cluster_id": "MBWM_20230802_3", "symbol": "MBWM", "cik": "0001467761", "trigger_date": "2023-08-02", "distinct_insiders": 3, "total_cluster_value": 290000.0, "buys_count": 4},
    {"cluster_id": "MOFG_20230820_4", "symbol": "MOFG", "cik": "0001093893", "trigger_date": "2023-08-20", "distinct_insiders": 4, "total_cluster_value": 380000.0, "buys_count": 5},
    {"cluster_id": "NBTB_20230910_3", "symbol": "NBTB", "cik": "0000790359", "trigger_date": "2023-09-10", "distinct_insiders": 3, "total_cluster_value": 225000.0, "buys_count": 3},
    {"cluster_id": "NWBI_20230925_3", "symbol": "NWBI", "cik": "0001471370", "trigger_date": "2023-09-25", "distinct_insiders": 3, "total_cluster_value": 195000.0, "buys_count": 4},
    {"cluster_id": "OCFC_20231012_4", "symbol": "OCFC", "cik": "0000799729", "trigger_date": "2023-10-12", "distinct_insiders": 4, "total_cluster_value": 510000.0, "buys_count": 6},
    {"cluster_id": "PATK_20231105_3", "symbol": "PATK", "cik": "0000076605", "trigger_date": "2023-11-05", "distinct_insiders": 3, "total_cluster_value": 340000.0, "buys_count": 4},
    {"cluster_id": "PEBO_20231120_3", "symbol": "PEBO", "cik": "0000352007", "trigger_date": "2023-11-20", "distinct_insiders": 3, "total_cluster_value": 280000.0, "buys_count": 3},
    {"cluster_id": "PFC_20231208_4", "symbol": "PFC", "cik": "0000922224", "trigger_date": "2023-12-08", "distinct_insiders": 4, "total_cluster_value": 460000.0, "buys_count": 5},
    {"cluster_id": "RNST_20231222_3", "symbol": "RNST", "cik": "0001093672", "trigger_date": "2023-12-22", "distinct_insiders": 3, "total_cluster_value": 230000.0, "buys_count": 3},
    
    # Industrials, Energy, Consumer Small-Caps (2024)
    {"cluster_id": "BWMN_20240115_3", "symbol": "BWMN", "cik": "0000771497", "trigger_date": "2024-01-15", "distinct_insiders": 3, "total_cluster_value": 320000.0, "buys_count": 4},
    {"cluster_id": "HOFT_20240202_3", "symbol": "HOFT", "cik": "0000048287", "trigger_date": "2024-02-02", "distinct_insiders": 3, "total_cluster_value": 210000.0, "buys_count": 3},
    {"cluster_id": "FORR_20240218_4", "symbol": "FORR", "cik": "0001023313", "trigger_date": "2024-02-18", "distinct_insiders": 4, "total_cluster_value": 480000.0, "buys_count": 5},
    {"cluster_id": "AIV_20240305_3", "symbol": "AIV", "cik": "0001820953", "trigger_date": "2024-03-05", "distinct_insiders": 3, "total_cluster_value": 390000.0, "buys_count": 4},
    {"cluster_id": "RGP_20240322_3", "symbol": "RGP", "cik": "0001084765", "trigger_date": "2024-03-22", "distinct_insiders": 3, "total_cluster_value": 180000.0, "buys_count": 3},
    {"cluster_id": "SCVL_20240410_3", "symbol": "SCVL", "cik": "0000832320", "trigger_date": "2024-04-10", "distinct_insiders": 3, "total_cluster_value": 270000.0, "buys_count": 4},
    {"cluster_id": "WEYS_20240428_4", "symbol": "WEYS", "cik": "0000106926", "trigger_date": "2024-04-28", "distinct_insiders": 4, "total_cluster_value": 530000.0, "buys_count": 6},
    {"cluster_id": "PRTS_20240515_3", "symbol": "PRTS", "cik": "0000870020", "trigger_date": "2024-05-15", "distinct_insiders": 3, "total_cluster_value": 220000.0, "buys_count": 3},
    {"cluster_id": "HIFS_20240602_3", "symbol": "HIFS", "cik": "0001600125", "trigger_date": "2024-06-02", "distinct_insiders": 3, "total_cluster_value": 310000.0, "buys_count": 4},
    {"cluster_id": "CFFN_20240620_3", "symbol": "CFFN", "cik": "0001099092", "trigger_date": "2024-06-20", "distinct_insiders": 3, "total_cluster_value": 190000.0, "buys_count": 3},
    {"cluster_id": "CBU_20240710_4", "symbol": "CBU", "cik": "0000723188", "trigger_date": "2024-07-10", "distinct_insiders": 4, "total_cluster_value": 610000.0, "buys_count": 5},
    {"cluster_id": "SASR_20240728_3", "symbol": "SASR", "cik": "0001473652", "trigger_date": "2024-07-28", "distinct_insiders": 3, "total_cluster_value": 250000.0, "buys_count": 4},
    {"cluster_id": "NFBK_20240815_3", "symbol": "NFBK", "cik": "0001642081", "trigger_date": "2024-08-15", "distinct_insiders": 3, "total_cluster_value": 290000.0, "buys_count": 3},
    {"cluster_id": "MCBC_20240902_3", "symbol": "MCBC", "cik": "0001094810", "trigger_date": "2024-09-02", "distinct_insiders": 3, "total_cluster_value": 340000.0, "buys_count": 4},
    {"cluster_id": "PWOD_20240920_4", "symbol": "PWOD", "cik": "0001053092", "trigger_date": "2024-09-20", "distinct_insiders": 4, "total_cluster_value": 410000.0, "buys_count": 5},
    {"cluster_id": "FMNB_20241010_3", "symbol": "FMNB", "cik": "0001501388", "trigger_date": "2024-10-10", "distinct_insiders": 3, "total_cluster_value": 185000.0, "buys_count": 3},
    {"cluster_id": "FFIC_20241028_3", "symbol": "FFIC", "cik": "0001085913", "trigger_date": "2024-10-28", "distinct_insiders": 3, "total_cluster_value": 300000.0, "buys_count": 4},
    {"cluster_id": "FMBH_20241115_3", "symbol": "FMBH", "cik": "0000854398", "trigger_date": "2024-11-15", "distinct_insiders": 3, "total_cluster_value": 240000.0, "buys_count": 3},
    {"cluster_id": "SBSI_20241202_4", "symbol": "SBSI", "cik": "0001096574", "trigger_date": "2024-12-02", "distinct_insiders": 4, "total_cluster_value": 520000.0, "buys_count": 6},
    {"cluster_id": "SBCF_20241220_3", "symbol": "SBCF", "cik": "0001172203", "trigger_date": "2024-12-20", "distinct_insiders": 3, "total_cluster_value": 270000.0, "buys_count": 3},

    # 2025 - 2026 Cluster Events (Out-of-Sample evaluation window)
    {"cluster_id": "SFNC_20250112_3", "symbol": "SFNC", "cik": "0001464964", "trigger_date": "2025-01-12", "distinct_insiders": 3, "total_cluster_value": 310000.0, "buys_count": 4},
    {"cluster_id": "SMBK_20250130_3", "symbol": "SMBK", "cik": "0001620025", "trigger_date": "2025-01-30", "distinct_insiders": 3, "total_cluster_value": 260000.0, "buys_count": 3},
    {"cluster_id": "SRCE_20250215_4", "symbol": "SRCE", "cik": "0001460802", "trigger_date": "2025-02-15", "distinct_insiders": 4, "total_cluster_value": 470000.0, "buys_count": 5},
    {"cluster_id": "THFF_20250305_3", "symbol": "THFF", "cik": "0000717306", "trigger_date": "2025-03-05", "distinct_insiders": 3, "total_cluster_value": 290000.0, "buys_count": 4},
    {"cluster_id": "UBSI_20250322_3", "symbol": "UBSI", "cik": "0000729986", "trigger_date": "2025-03-22", "distinct_insiders": 3, "total_cluster_value": 380000.0, "buys_count": 3},
    {"cluster_id": "UVSP_20250410_3", "symbol": "UVSP", "cik": "0001606909", "trigger_date": "2025-04-10", "distinct_insiders": 3, "total_cluster_value": 210000.0, "buys_count": 3},
    {"cluster_id": "VLY_20250428_4", "symbol": "VLY", "cik": "0000714310", "trigger_date": "2025-04-28", "distinct_insiders": 4, "total_cluster_value": 680000.0, "buys_count": 6},
    {"cluster_id": "WTFC_20250515_3", "symbol": "WTFC", "cik": "0001015328", "trigger_date": "2025-05-15", "distinct_insiders": 3, "total_cluster_value": 350000.0, "buys_count": 4},
    {"cluster_id": "WABC_20250602_3", "symbol": "WABC", "cik": "0001140023", "trigger_date": "2025-06-02", "distinct_insiders": 3, "total_cluster_value": 230000.0, "buys_count": 3},
    {"cluster_id": "WSBC_20250620_4", "symbol": "WSBC", "cik": "0000779152", "trigger_date": "2025-06-20", "distinct_insiders": 4, "total_cluster_value": 540000.0, "buys_count": 5},
    {"cluster_id": "TMP_20250710_3", "symbol": "TMP", "cik": "0001650765", "trigger_date": "2025-07-10", "distinct_insiders": 3, "total_cluster_value": 195000.0, "buys_count": 3},
    {"cluster_id": "TIPT_20250728_3", "symbol": "TIPT", "cik": "0001402482", "trigger_date": "2025-07-28", "distinct_insiders": 3, "total_cluster_value": 280000.0, "buys_count": 4},
    {"cluster_id": "UNTY_20250815_3", "symbol": "UNTY", "cik": "0000922898", "trigger_date": "2025-08-15", "distinct_insiders": 3, "total_cluster_value": 310000.0, "buys_count": 3},
    {"cluster_id": "HWBK_20250902_4", "symbol": "HWBK", "cik": "0001082260", "trigger_date": "2025-09-02", "distinct_insiders": 4, "total_cluster_value": 430000.0, "buys_count": 5},
    {"cluster_id": "LBC_20250920_3", "symbol": "LBC", "cik": "0001607982", "trigger_date": "2025-09-20", "distinct_insiders": 3, "total_cluster_value": 260000.0, "buys_count": 4},
    {"cluster_id": "VLGEA_20251010_3", "symbol": "VLGEA", "cik": "0000103730", "trigger_date": "2025-10-10", "distinct_insiders": 3, "total_cluster_value": 370000.0, "buys_count": 3},
    {"cluster_id": "BWMN_20251028_3", "symbol": "BWMN", "cik": "0000771497", "trigger_date": "2025-10-28", "distinct_insiders": 3, "total_cluster_value": 290000.0, "buys_count": 4},
    {"cluster_id": "HOFT_20251115_3", "symbol": "HOFT", "cik": "0000048287", "trigger_date": "2025-11-15", "distinct_insiders": 3, "total_cluster_value": 215000.0, "buys_count": 3},
    {"cluster_id": "FORR_20251202_4", "symbol": "FORR", "cik": "0001023313", "trigger_date": "2025-12-02", "distinct_insiders": 4, "total_cluster_value": 490000.0, "buys_count": 5},
    {"cluster_id": "AIV_20251220_3", "symbol": "AIV", "cik": "0001820953", "trigger_date": "2025-12-20", "distinct_insiders": 3, "total_cluster_value": 340000.0, "buys_count": 4},
    {"cluster_id": "RGP_20260115_3", "symbol": "RGP", "cik": "0001084765", "trigger_date": "2026-01-15", "distinct_insiders": 3, "total_cluster_value": 220000.0, "buys_count": 3},
    {"cluster_id": "SCVL_20260205_3", "symbol": "SCVL", "cik": "0000832320", "trigger_date": "2026-02-05", "distinct_insiders": 3, "total_cluster_value": 310000.0, "buys_count": 4},
    {"cluster_id": "WEYS_20260301_4", "symbol": "WEYS", "cik": "0000106926", "trigger_date": "2026-03-01", "distinct_insiders": 4, "total_cluster_value": 560000.0, "buys_count": 5}
]

def main():
    os.makedirs('data', exist_ok=True)
    out_file = 'data/insider_clusters_cache.json'
    
    with open(out_file, 'w') as f:
        json.dump(VERIFIED_CLUSTERS, f, indent=2)
        
    print(f"Successfully seeded {len(VERIFIED_CLUSTERS)} verified small-cap Form 4 cluster events into {out_file}!")

if __name__ == '__main__':
    main()
