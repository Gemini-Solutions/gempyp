import pandas as pd


# for handling data formatting
def dateFormatHandling(src_df,tgt_df):
    try:
        src_df = formatingDate(src_df)
        tgt_df = formatingDate(tgt_df) 
        # print("tgt_df",tgt_df.dtypes)
        return src_df, tgt_df
    except Exception:
        raise Exception

def formatingDate(df):
    columns = df.select_dtypes(include=['datetime64']).columns
    for column in list(columns):
        df[column] = pd.to_datetime(df[column],errors='ignore')
    return df

def columnCompare(src_df, tgt_df, keys, compare_keys):
    """we are trying to get list of columns which we dont want to compare and droping them"""
    columns = keys+compare_keys
    src_df = src_df[columns]
    tgt_df = tgt_df[columns]
    return src_df, tgt_df