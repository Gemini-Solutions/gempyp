import traceback
from gempyp.libs.common import get_reason_of_failure
import numpy
import math


def df_compare(df_1, df_2, key, logger, reporter, configData):

    try:
            logger.info("In df_compare Function")
            headers = list(set(list(df_1.columns)) - set(key))
            df_1['key'] = df_1[key].apply(
                lambda row: '--'.join(row.values.astype(str)), axis=1)
            df_2['key'] = df_2[key].apply(
                lambda row: '--'.join(row.values.astype(str)), axis=1)
            df_1.set_index('key', inplace=True)
            df_2.set_index('key', inplace=True)
            df_1.drop(key, axis=1, inplace=True)
            df_2.drop(key, axis=1, inplace=True)
            src_key_values = df_1.index.values
            tgt_key_values = df_2.index.values
            
            common_keys = list(set(src_key_values) & set(tgt_key_values))
            keys_only_in_src = list(
                set(src_key_values) - set(tgt_key_values))
            keys_only_in_tgt = list(
                set(tgt_key_values) - set(src_key_values))
            df_1.drop(keys_only_in_src,inplace=True)
            df_2.drop(keys_only_in_tgt,inplace=True)
            """calling src and tgt for getting different keys"""
            src_key_dict = addDiffKeysDict(keys_only_in_src, "Source", key)
            tgt_key_dict = addDiffKeysDict(keys_only_in_tgt, "Target", key)
            for keys in src_key_dict.keys():
                src_key_dict[keys] = src_key_dict[keys] + tgt_key_dict[keys]
            df_1.index.astype(str)
            df_2.index.astype(str)
            df_1.sort_values(by=['key'],inplace=True)
            df_2.sort_values(by=['key'],inplace=True)
            common_keys.sort()
            value_dict = getValueDict(df_1,df_2,common_keys,headers,key,configData)
            keys_length = {"keys_only_in_src":len(keys_only_in_src),"keys_only_in_tgt":len(keys_only_in_tgt)}
            return value_dict, src_key_dict, common_keys, keys_length
    except Exception as e:
            traceback.print_exc()
            reporter.addMisc(
                "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))

def addDiffKeysDict(_list, db, keys):

    key_dict = {}
    dict1 = {'REASON OF FAILURE': []}
    li1 = []
    for i in keys:
        li1.append([])            
    if _list:
        for i in _list:
            li = i.split("--")
            for i in range(len(li)):
                key = keys[i]
                li1[i].append(li[i])
                value = li1[i]
                key_dict[key] = value
            dict1.get("REASON OF FAILURE").append(
                f"keys only in {db}")
    
    key_dict.update(dict1)
    return key_dict


def compareValues(commonList: list,df_1,df_2, headers,keys,configData):
            print("In compareValues Function")
            dummy_dict = { 'Column_Name':[],'Source_Value':[],'Target_Value':[],'REASON OF FAILURE':[]}
            comm_dict ={}

            if commonList:
                for key_val in commonList:
                    for field in headers:
                        src_val = df_1.loc[key_val,field]
                        tgt_val = df_2.loc[key_val,field]
                        if src_val == src_val or tgt_val == tgt_val:
                            if "THRESHOLD" in configData:
                                # self.reporter.addMisc("Threshold",str(self.configData["THRESHOLD"]))
                                if type(src_val)== numpy.float64 and math.isnan(src_val) == False:
                                    src_val = truncate(src_val,int(configData["THRESHOLD"]))
                                if type(tgt_val)== numpy.float64 and math.isnan(tgt_val) == False:
                                    tgt_val = truncate(tgt_val,int(configData["THRESHOLD"]))
                                
                            if src_val != tgt_val and type(src_val)==type(tgt_val):
                                    
                                li = key_val.split('--')
                                for i in range(len(li)):
                                    key = keys[i]
                                    li1 = []
                                    li1.append(li[i])
                                    comm_dict[key] = comm_dict.get(key,[]) + li1
                                dummy_dict.get('Column_Name').append(field)
                                dummy_dict.get('Source_Value').append(src_val)
                                dummy_dict.get('Target_Value').append(tgt_val)
                                dummy_dict.get('REASON OF FAILURE').append("Difference In Value")                       
                                    
                            elif type(src_val)!= type(tgt_val):
                                        
                                li = key_val.split('--')
                                for i in range(len(li)):
                                    key = keys[i]
                                    li1 = []
                                    li1.append(li[i])
                                    comm_dict[key] = comm_dict.get(key,[]) + li1
                                dummy_dict.get('Column_Name').append(field)
                                dummy_dict.get('Source_Value').append(src_val)
                                dummy_dict.get('Target_Value').append(tgt_val)
                                dummy_dict.get('REASON OF FAILURE').append("Difference In Datatype")
                comm_dict.update(dummy_dict)               
                return comm_dict

def truncate(f, n):

        return math.floor(f * 10 ** n) / 10 ** n

def getValueDict(df_1,df_2,common_keys,headers,key,configData):
        
        splitSize = 100000
        common_keys_splited = [common_keys[x:x+splitSize] for x in range(0, len(common_keys), splitSize)]
        df_1_splited = [df_1[x:x+splitSize] for x in range(0, len(df_1), splitSize)]
        df_2_splited = [df_2[x:x+splitSize] for x in range(0, len(df_2), splitSize)]
        final_value_diffs = {}
        for i in range(len(common_keys_splited)):
            chunk_diffs = compareValues(common_keys_splited[i],df_1_splited[i],df_2_splited[i],headers,key,configData)
            for keys in chunk_diffs.keys():
                if keys in final_value_diffs.keys():
                    final_value_diffs[keys] = final_value_diffs[keys] + chunk_diffs[keys]
                else:
                    final_value_diffs[keys] = chunk_diffs[keys]
        return final_value_diffs