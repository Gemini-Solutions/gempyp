import pandas as pd
from gempyp.libs.common import get_reason_of_failure
import traceback
from gempyp.libs.enums.status import status


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

def skipColumn(skip_column,src_df,tgt_df,key,reporter):
            try:
                skip_column = skip_column.split(',')
                src_columns = src_df.columns
                tgt_columns = tgt_df.columns
                src_skip_columns = list(set(src_columns) & set(skip_column))
                tgt_skip_columns = list(set(tgt_columns) & set(skip_column))
                flag = False
                for i in key:
                    if i in skip_column:
                        flag = True
                        break
                if flag:
                    reporter.addRow("Column Given for Skip are Present in Keys Tag","Aborting Skip Columns",status.INFO)
                    return src_df,tgt_df
                else:
                    # for i in skip_column:
                    src_df.drop(src_skip_columns,axis=1,inplace=True)
                        # del src_df[i]
                    # for i in skip_column:
                    tgt_df.drop(tgt_skip_columns,axis=1,inplace=True)
                        # del tgt_df[i]
                    # headers = list(set(headers)-set(skip_column))
                    return src_df,tgt_df
            except Exception as e:
                print(e)
                reporter.addRow("While Skipping Columns",get_reason_of_failure(traceback.format_exc(), e),status.INFO)
                return src_df, tgt_df