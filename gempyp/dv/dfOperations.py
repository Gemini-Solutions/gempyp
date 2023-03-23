import pandas as pd


# for handling data formatting
def dateFormatHandling(src_df,tgt_df):
    try:
        # print("tgt_df",tgt_df.dtypes)
        src_df = formatingDate(src_df)
        tgt_df = formatingDate(tgt_df) 
        # print("tgt_df",tgt_df.dtypes)
        return src_df, tgt_df
    except Exception:
        raise Exception

def formatingDate(df):
    columns = df.select_dtypes(include=['object']).columns
    for column in list(columns):
        df[column] = pd.to_datetime(df[column],errors='ignore')
    return df
