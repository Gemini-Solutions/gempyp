import traceback
from gempyp.libs.common import get_reason_of_failure
import numpy
import math
import itertools
import collections
from gempyp.libs.enums.status import status
import time
import pandas as pd


def df_compare(src_df, tgt_df, key, logger, reporter, configData):
    try:
        logger.info("In df_compare Function")
        headers = list(set(list(src_df.columns)) - set(key))
        src_df["key"] = src_df[key].apply(
            lambda row: "----".join(row.values.astype(str)), axis=1
        )
        tgt_df["key"] = tgt_df[key].apply(
            lambda row: "----".join(row.values.astype(str)), axis=1
        )
        src_df.set_index("key", inplace=True)
        tgt_df.set_index("key", inplace=True)
        src_df.drop(key, axis=1, inplace=True)
        tgt_df.drop(key, axis=1, inplace=True)
        src_key_values = src_df.index.values
        tgt_key_values = tgt_df.index.values
        common_keys = list(set(src_key_values) & set(tgt_key_values))
        keys_only_in_src = list(set(src_key_values) - set(tgt_key_values))
        keys_only_in_tgt = list(set(tgt_key_values) - set(src_key_values))
        src_df.drop(keys_only_in_src, inplace=True)
        tgt_df.drop(keys_only_in_tgt, inplace=True)
        """calling src and tgt for getting different keys"""
        src_key_dict = addDiffKeysDict(keys_only_in_src, "Source", key, logger)
        tgt_key_dict = addDiffKeysDict(keys_only_in_tgt, "Target", key, logger)
        # for keys in src_key_dict.keys():
        #     src_key_dict[keys] = src_key_dict[keys] + tgt_key_dict[keys]
        diff_keys_dict = collections.defaultdict(list)
        for keys, val in itertools.chain(src_key_dict.items(), tgt_key_dict.items()):
            diff_keys_dict[keys] += val
        diff_keys_dict = dict(diff_keys_dict)
        src_df.index.astype(str)
        tgt_df.index.astype(str)
        src_df.sort_values(by=["key"], inplace=True)
        tgt_df.sort_values(by=["key"], inplace=True)
        common_keys.sort()
        value_dict = getValueDict(
            src_df, tgt_df, common_keys, headers, key, configData, logger, reporter
        )
        keys_length = {
            "keys_only_in_src": len(keys_only_in_src),
            "keys_only_in_tgt": len(keys_only_in_tgt),
            "common_keys": len(common_keys)
        }
        if "TOLERANCE" in configData:
            reporter.addMisc("TOLERANCE",str(configData.get("TOLERANCE",0)))
        if "ROUND_OFF" in configData:
            reporter.addMisc("ROUND OFF",str(configData.get("ROUND_OFF",0)))
        return value_dict, diff_keys_dict, keys_length
    except Exception as e:
        traceback.print_exc()
        reporter.addRow("Comparing data", "Error occurred", status.ERR)
        reporter.addMisc(
            "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e)
        )


def addDiffKeysDict(_list, db, keys, logger):
    logger.info("In addDiffKeysDict Function")
    key_dict = {}
    dict1 = {"Reason-of-Failure": []}
    li1 = []
    for i in keys:
        li1.append([])
    if _list:
        for i in _list:
            li = i.split("----")
            for i in range(len(li)):
                key = keys[i]
                li1[i].append(li[i])
                value = li1[i]
                key_dict[key] = value
            dict1.get("Reason-of-Failure").append(f"keys only in {db}")
    key_dict.update(dict1)
    return key_dict


def compareValues(commonList: list, src_df, tgt_df, headers, keys, configData, logger,cut_out,count):
    if "ROUND_OFF" in configData:
        for column in src_df.columns:
            if src_df[column].dtype == numpy.float64:
                src_df[column] = src_df[column].round(int(configData.get("ROUND_OFF")))
        for column in tgt_df.columns:
            if tgt_df[column].dtype == numpy.float64:
                tgt_df[column] = tgt_df[column].round(int(configData.get("ROUND_OFF")))

    all_differences_df = []
    mask = ~((src_df == tgt_df) | (src_df.isna() & tgt_df.isna()))
    dummy_response_dict = {
        "Column-Name": [],
        "Source-Value": [],
        "Target-Value": [],
        "Reason-of-Failure": [],
        }
    for key in keys:
        dummy_response_dict[key] = []
    if (mask.isna() | (mask == False)).all().all():
        return dummy_response_dict
    for column in headers:
        if mask[column].any():
                diff_values_df = pd.DataFrame({
                'Keys----map': src_df.index[mask[column]],
                'Column-Name': column,
                'Source-Value': src_df[column][mask[column]].values,
                'Target-Value': tgt_df[column][mask[column]].values,
                'Reason-of-Failure': 'Difference In Value'
            })
        else:
            continue
        all_differences_df.append(diff_values_df)
    if all_differences_df:
        result_df = pd.concat(all_differences_df, ignore_index=True)
    else:
        result_df = pd.DataFrame(columns=['Keys----map', 'Column-Name', 'Source-Value', 'Target-Value', 'Reason-of-Failure'])
    new_mask = result_df['Source-Value'].astype(str) == result_df["Target-Value"].astype(str)

    result_df.loc[new_mask,'Reason-of-Failure'] = "Difference In Datatype"
    if "TOLERANCE" in configData:
        result_df['Source-Value'] = pd.to_numeric(result_df['Source-Value'], errors='coerce')
        result_df['Target-Value'] = pd.to_numeric(result_df['Target-Value'], errors='coerce')

        # Filter the DataFrame
        filtered_df = result_df[
            result_df['Source-Value'].notna() &  # Check if src_val is not NaN
            result_df['Target-Value'].notna() &  # Check if tgt_val is not NaN
            (result_df['Reason-of-Failure'] == 'Difference In Value')  # Check for diff_type 'A'
        ]
        # Calculate the difference
        filtered_df['difference'] = (filtered_df['Source-Value'] - filtered_df['Target-Value']).abs()

        threshold = float(configData.get("TOLERANCE",0))

        # Drop rows where the difference is smaller than the threshold
        filtered_df = filtered_df[filtered_df['difference'] <= threshold]
        result_df = result_df[~result_df['Keys----map'].isin(filtered_df['Keys----map'])]
    if result_df.empty:
        return dummy_response_dict
    split_columns = result_df['Keys----map'].str.split('----', expand=True)
    for i, key in enumerate(keys):
        result_df[key] = split_columns[i]
    result_df.drop('Keys----map', axis=1, inplace=True)

    final_dict = result_df.to_dict(orient='list')
    return final_dict


def truncate(f, n):
    return math.floor(f * 10**n) / 10**n


def getValueDict(src_df, tgt_df, common_keys, headers, key, configData, logger, reporter):
    logger.info("In getValueDict Function")
    splitSize = 100000
    """this code is for deciding cutout range"""
    if len(common_keys) > 100000:
        length = (10*len(common_keys))//100
        cut_out = configData.get('CUT_OUT',length)
    else:
        cut_out = configData.get('CUT_OUT',100000)
        
    common_keys_splited = [
        common_keys[x : x + splitSize] for x in range(0, len(common_keys), splitSize)
    ]
    src_df_splited = [src_df[x : x + splitSize] for x in range(0, len(src_df), splitSize)]
    tgt_df_splited = [tgt_df[x : x + splitSize] for x in range(0, len(tgt_df), splitSize)]
    # final_value_diffs = collections.defaultdict(list)
    final_value_diffs = {
            "Column-Name": [],
            "Source-Value": [],
            "Target-Value": [],
            "Reason-of-Failure": [],
        }
    count = 0
    for i in range(len(common_keys_splited)):
        logger.info(time.time())
        # data = {"common_keys_splited":common_keys_splited[i],"src_df_splited":src_df_splited[i],"tgt_df_splited":tgt_df_splited[i],"headers":headers,"key":key,"configData":configData,"logger":logger,"cut_out":cut_out,"count":count}
        chunk_diffs = compareValues(
            common_keys_splited[i],
            src_df_splited[i],
            tgt_df_splited[i],
            headers,
            key,
            configData,
            logger,
            cut_out,
            count
        )
        for keys in chunk_diffs.keys():
            if keys in final_value_diffs.keys():
                final_value_diffs[keys] = final_value_diffs[keys] + chunk_diffs[keys]
            else:
                final_value_diffs[keys] = chunk_diffs[keys]
        count = len(final_value_diffs["Reason-of-Failure"])
        if count > int(cut_out):
            reporter.addRow("Stopping execution","Mismatch count is greater than {}".format(cut_out),status.INFO)
            break
        
        logger.info(time.time())
    return final_value_diffs
