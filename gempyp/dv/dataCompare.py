import traceback
from gempyp.libs.common import get_reason_of_failure
import numpy
import math
import itertools
import collections
from gempyp.libs.enums.status import status
import time
import pandas as pd
from gempyp.libs.common import get_reason_of_failure
from gempyp.dv.writeResultFile import writeExcel

from gempyp.dv.dfOperations import dateFormatHandling, columnCompare, skipColumn, matchKeys, matchCase


def df_compare(src_df, tgt_df, key, reporter, configData={}):
    """
    src_df --------> dataFrame
    tgt_df --------> dataFrame
    key    --------> list
    reporter ------> object
    configData ----> dictionary
    """
    try:
        reporter.logger.info("In df_compare Function")
        tgt_columns = list(tgt_df.columns)
        src_columns = list(src_df.columns)
        if "COLUMN_MAP" in configData:
            tgt_df.rename(columns=eval(
                configData["COLUMN_MAP"]), inplace=True)
            tgt_columns = list(tgt_df.columns)
        matchKeys(src_columns, "SOURCE",key,reporter)
        matchKeys(tgt_columns, "TARGET",key,reporter)

        if 'SKIP_COLUMN' in configData:
            src_df, tgt_df = skipColumn(checkingList(configData.get('SKIP_COLUMN')),src_df,tgt_df,key,reporter)
            src_columns = list(src_df.columns)
            tgt_columns = list(tgt_df.columns)
        
        if src_columns == tgt_columns:
            pass
        else:
            reporter.logger.info(
                "--------Same Column not Present in Both Table--------")
            reporter.addRow(
                "Same Columns in Table", "Not Found", status.ERR)
            raise Exception("Same Columns Not Found")

        """deleting duplicates from df and keeping last ones"""
        reporter.logger.info("Removing Duplicates Rows")
        if "COMPARE_COLUMN" in configData:
            compare_column = checkingList(configData.get("COMPARE_COLUMN",''))
            src_df, tgt_df = columnCompare(src_df, tgt_df, key, compare_column)
        # hadling case insensitivity
        if 'MATCH_CASE' in configData:
            src_df, tgt_df = matchCase(src_df,tgt_df,reporter,configData)

        # date format handling
        src_df, tgt_df = dateFormatHandling(src_df, tgt_df)

        source_duplicates_df, src_dup_len = getDuplicateKeysDf(src_df, "SOURCE",key, reporter)
        target_duplicates_df, tgt_dup_len = getDuplicateKeysDf(tgt_df, "TARGET",key, reporter)
        dup_keys_length = src_dup_len + tgt_dup_len
        duplicate_keys_df = pd.concat([source_duplicates_df , target_duplicates_df ], axis=0, ignore_index=True)

        src_df.drop_duplicates(
                subset=key, keep='last', inplace=True)
        tgt_df.drop_duplicates(
                subset=key, keep='last', inplace=True)
        
    except Exception as e:
        traceback.print_exc()
        reporter.addMisc(
            "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e)
        )
        return
    try:
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
        src_key_dict = addDiffKeysDict(keys_only_in_src, "Source", key, reporter)
        tgt_key_dict = addDiffKeysDict(keys_only_in_tgt, "Target", key, reporter)
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
            src_df, tgt_df, common_keys, headers, key, configData, reporter
        )
        keys_length = {
            "keys_only_in_src": len(keys_only_in_src),
            "keys_only_in_tgt": len(keys_only_in_tgt),
            "common_keys": len(common_keys),
            "dup_keys_length": dup_keys_length,
            "key_check": len(diff_keys_dict["Reason-of-Failure"]),
            "value_check": len(value_dict["Reason-of-Failure"])
        }
        if "TOLERANCE" in configData:
            reporter.addMisc("TOLERANCE",str(configData.get("TOLERANCE",0)))
        if "ROUND_OFF" in configData:
            reporter.addMisc("ROUND OFF",str(configData.get("ROUND_OFF",0)))
        
        value_df = pd.DataFrame(value_dict)
        keys_df = pd.DataFrame(diff_keys_dict)
        df = pd.concat([value_df, keys_df, duplicate_keys_df ], axis=0, ignore_index=True)
        writeExcel(df,keys_length,reporter,configData)
        # return df, keys_length
        return
    except Exception as e:
        traceback.print_exc()
        reporter.addRow("Comparing Data", "Error Occured", status.ERR)
        reporter.addMisc(
            "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e)
        )
        return


def addDiffKeysDict(_list, db, keys,reporter):
    reporter.logger.info("In addDiffKeysDict Function")
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


def compareValues(commonList: list, src_df, tgt_df, headers, keys, configData,cut_out,count,reporter):
    reporter.logger.info("In compareValues Function")
    dummy_dict = {
        "Column-Name": [],
        "Source-Value": [],
        "Target-Value": [],
        "Reason-of-Failure": [],
    }
    comm_dict = {}

    if commonList:
        for key_val in commonList:
            for field in headers:
                src_val = src_df.loc[key_val, field]
                tgt_val = tgt_df.loc[key_val, field]
                if src_val == src_val or tgt_val == tgt_val:
                    if "ROUND_OFF" in configData:
                        # self.reporter.addMisc("",str(self.configData["THRESHOLD"]))
                        if (
                            type(src_val) == numpy.float64
                            and math.isnan(src_val) == False
                        ):
                            src_val = truncate(src_val, int(configData["ROUND_OFF"]))
                        if (
                            type(tgt_val) == numpy.float64
                            and math.isnan(tgt_val) == False
                        ):
                            tgt_val = truncate(tgt_val, int(configData["ROUND_OFF"]))

                    if type(src_val) == numpy.float64 and type(tgt_val) == numpy.float64:
                        if math.isnan(src_val) == False and math.isnan(tgt_val) == False:
                            if src_val - tgt_val > float(configData.get("TOLERANCE",0)):
                                li = key_val.split("----")
                                #this is for getting the key value
                                for i in range(len(li)):
                                    key = keys[i]
                                    li1 = []
                                    li1.append(li[i])
                                    comm_dict[key] = comm_dict.get(key, []) + li1
                                dummy_dict.get("Column-Name").append(field)
                                dummy_dict.get("Source-Value").append(src_val)
                                dummy_dict.get("Target-Value").append(tgt_val)
                                dummy_dict.get("Reason-of-Failure").append(
                                    "Difference In Value"
                                    )   

                    elif src_val != tgt_val and type(src_val) == type(tgt_val):
                        li = key_val.split("----")
                        for i in range(len(li)):
                            key = keys[i]
                            li1 = []
                            li1.append(li[i])
                            comm_dict[key] = comm_dict.get(key, []) + li1
                        dummy_dict.get("Column-Name").append(field)
                        dummy_dict.get("Source-Value").append(src_val)
                        dummy_dict.get("Target-Value").append(tgt_val)
                        dummy_dict.get("Reason-of-Failure").append(
                            "Difference In Value"
                        )

                    elif type(src_val) != type(tgt_val):
                        li = key_val.split("----")
                        for i in range(len(li)):
                            key = keys[i]
                            li1 = []
                            li1.append(li[i])
                            comm_dict[key] = comm_dict.get(key, []) + li1
                        dummy_dict.get("Column-Name").append(field)
                        dummy_dict.get("Source-Value").append(src_val)
                        dummy_dict.get("Target-Value").append(tgt_val)
                        dummy_dict.get("Reason-of-Failure").append(
                            "Difference In Datatype"
                        )
            if count + len(dummy_dict['Reason-of-Failure']) > int(cut_out):
                break   
        comm_dict.update(dummy_dict)
        return comm_dict


def truncate(f, n):
    return math.floor(f * 10**n) / 10**n


def getValueDict(src_df, tgt_df, common_keys, headers, key, configData, reporter):
    reporter.logger.info("In getValueDict Function")
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
        reporter.logger.info(time.time())
        # data = {"common_keys_splited":common_keys_splited[i],"src_df_splited":src_df_splited[i],"tgt_df_splited":tgt_df_splited[i],"headers":headers,"key":key,"configData":configData,"logger":logger,"cut_out":cut_out,"count":count}
        chunk_diffs = compareValues(
            common_keys_splited[i],
            src_df_splited[i],
            tgt_df_splited[i],
            headers,
            key,
            configData,
            cut_out,
            count,
            reporter
        )
        for keys in chunk_diffs.keys():
            if keys in final_value_diffs.keys():
                final_value_diffs[keys] = final_value_diffs[keys] + chunk_diffs[keys]
            else:
                final_value_diffs[keys] = chunk_diffs[keys]
        # for key, val in itertools.chain(final_value_diffs.items(), chunk_diffs.items()):
        # final_value_diffs[key] += val
        # final_value_diffs = dict(final_value_diffs)
        count = len(final_value_diffs["Reason-of-Failure"])
        if count > int(cut_out):
            reporter.addRow("Stopping Execution","Mismatch Count is Greater than {}".format(cut_out),status.INFO)
            break
        
        reporter.logger.info(time.time())
    return final_value_diffs

def getDuplicateKeysDf(df, type, keys, reporter):

        reporter.logger.info("Checking Dulicates Keys")
        dup_df = df[df[keys].duplicated(keep=False)]

        dup_keys_df = dup_df[keys]
        dup_length = len(dup_keys_df)
        dup_keys_df.drop_duplicates(
                keep='last', inplace=True)
        dup_keys_df['Reason-of-Failure'] = f'Duplicate Key in {type}'
        if len(dup_keys_df['Reason-of-Failure']) > 0:
            reporter.addRow(f"Checking for Duplicates Keys in {type}",f"Found Duplicate Keys in {type}",status.FAIL)
        return dup_keys_df, dup_length

def checkingList(data)->list:
    if type(data) == str:
        data = data.split(',')
    return data

