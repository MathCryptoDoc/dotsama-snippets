# Copyright 2022 https://www.math-crypto.com -- GNU General Public License

import pandas as pd
import numpy as np

def read_1kv_json(json_dir):
    """
    Read dumped json files from the 1kv backend.
    """
    df_s = []
    for f in list(json_dir.glob('*.feather')):
        datetime = f.stem
        df = pd.read_feather(f)
        df['datetime'] = datetime
        df = df.reset_index(drop=True)
        df_s.append(df)
    df_all = pd.concat(df_s).reset_index(drop=True)
    df_all['datetime'] = pd.to_datetime(df_all['score.updated'], unit='ms')
    return df_all 

def read_onchain_erareward_files(era_tmp_dir):
    """
    Read on-chain reward points that were dumped as feather files by active_eras.py
    """
    first = True    
    for f in sorted(era_tmp_dir.glob("*.feather")):    
        df_f = pd.read_feather(f)
        if first:
            df_all = df_f
            first = False
        else:
            df_all = pd.concat([df_all, df_f], ignore_index=True).drop_duplicates().reset_index(drop=True)
            # Detect same era address and take max (this can happen if era was not finished yet when querying chain)
            # From https://stackoverflow.com/a/40629420 - cool trick to select only max points 
            df_all = df_all.sort_values('points', ascending=False).drop_duplicates(['address','era'], keep="first")
            
            df_all = df_all.sort_values(["address", "era"])
            print(f"Number of rows: {len(df_all)}")
    return df_all

def read_onchain_era_start_file(era_start_file):
    """
    The ActiveEra storage function returns the start of the era.
    This gets dumped together with the era points when calling active_eras.py
    """
    df_start = pd.read_feather(era_start_file)
    df_start["datetime"] = pd.to_datetime(df_start["start"], unit="ms")
    return df_start    


def calc_inclusion_percentage(df_all, delta):
    """
    Calculate the percentage when validator was active for delta eras.
    Done for all eras in a sliding window [era-delta+1, era].
    # TODO: can be faster - calc from df_era and slice over all addresses (replace > = by True, and sum in window)
    """
    eras = df_all['era'].unique()
    max_era = np.max(eras) 
    min_era = np.min(eras)     
    addr = df_all['address'].unique()
        
    pcts = []
    for address in addr:
        pct_cur = {"address": address}
        df_cur = df_all[df_all['address'] == address]        
        for end_era in range(max_era, min_era+delta-1, -1):          
            pct_cur[end_era] = len( df_cur[(df_cur['era'] <= end_era) & (df_cur['era'] >= end_era-delta+1)] ) / delta
        pcts.append(pct_cur)

    return pd.DataFrame(pcts).set_index("address", verify_integrity=True)


def calc_inclusion_scores(df_incl, LOW_Q=0.20, UPP_Q=0.75, SCORE_WEIGHT=100):
    """
    Calculate the scores from the inclusion percentage
    """
    quant = df_incl.quantile([LOW_Q, UPP_Q])

    df_score = (df_incl - quant.loc[LOW_Q])/(quant.loc[UPP_Q] - quant.loc[LOW_Q])
    filt_low = df_incl<=quant.loc[LOW_Q]
    filt_high = df_incl>=quant.loc[UPP_Q]
    df_score[filt_low] = 0
    df_score[filt_high] = 1
    return (1-df_score) * SCORE_WEIGHT

def replace_era_by_timestamp(df, known_era, known_time, DURATION_EPOCH):
    """
    Calculate time stamps of the eras in df by a reference value.
    The columns of df should be eras (hence a df is wide).
    """
    eras = pd.to_numeric(df.columns).values
    eras_start = known_time + (eras  - known_era)*DURATION_EPOCH
    df_new = df.copy()
    df_new.columns = eras_start
    return df_new