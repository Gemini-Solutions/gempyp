import json
import logging as logger
import ast
import re
import gempyp.pyprest.compareFunctions as cf



def formatRespBody(response_body):
    """Encode/decode the response body"""
    if not isinstance(response_body, list):
        try:
            formatted_response_body = json.loads(response_body.decode("utf-8"))
            logger.info("keycheck ----- 1")
        except Exception:
            try:
                formatted_response_body = json.loads(ast.literal_eval(response_body.decode("utf-8")))
                logger.info("keycheck ----- 2")
            except Exception:
                try: 
                    formatted_response_body = json.loads(str(response_body.encode("utf-8")))
                    if "b'" in formatted_response_body:
                        formatted_response_body = formatted_response_body.strip("b'").strip("'")
                    logger.info("keycheck ----- 3")
                except Exception:
                    try:
                        formatted_response_body = json.loads(response_body)
                    except Exception as e:
                        formatted_response_body = response_body

    else:
        formatted_response_body = response_body
    return formatted_response_body


# not able to implement recursion in case of other 
def fetchValueOfKey(json_, key_partition_list, key_search_result, final_key_value={}):
    """
    Get values of the required keys from the response json"""

    logger.info("===========Fetching values from response ============")
    regex_each = re.compile(r".*\[\beach\b\]")
    regex_int = re.compile(r".*\[\d+\]")
    actual_key = ".".join(key_partition_list)
    flag = 0
    if key_search_result == "FOUND" or "MISSING IN " in key_search_result:
        for key in key_partition_list:
            if re.match(regex_each, key):
                each_value_list = []
                br_index = key.find('[')
                key_val = key[:br_index]
                if key_val != "response" or key_val != "legacy":
                    json_ = json_[key_val]
                for each_value in json_:
                    index_of_key = key_partition_list.index(key)
                    value_returned = getValuesForEach(each_value, key_partition_list[int(index_of_key) + 1:])
                    each_value_list.append(value_returned)
                del key_partition_list[int(index_of_key) + 1:]
                flag = 1
            elif re.match(regex_int, key):
                br_start = key.find('[')
                br_end = key.find(']')
                key_val = key[:br_start]
                key_num = int(key[br_start + 1:br_end])
                key_num, json_ = getNestedListData(key, json_, key_val)

                if key_val == "response" or key_val=="legacy" and isinstance(json_, list) :
                    json_ = json_[key_num]
                else:
                    json_ = json_[key_val][key_num]
            else:
                if isinstance(json_, str) and json_ != "":
                    json_ = json.dumps(json_)
                if json_ != "":
                    if "response" == key.lower() or "legacy" == key.lower():
                        json_ = json_
                    else:
                        json_ = json_[key]
                if json_ is None:
                    json_ = "null"
        if flag != 1:
            final_key_value[actual_key] = json_
        else:
            final_key_value[actual_key] = each_value_list
        
        return final_key_value


def getValuesForEach(each_value_dict, keys_to_fetch):
    """Getting values in case of "each operator" """
    logger.info(f"Keys to be fetched from response - {keys_to_fetch}")
    for key in keys_to_fetch:
        if key in each_value_dict:
            each_value_dict = each_value_dict[key]
            if each_value_dict is None:
                each_value_dict = "null"
                break
        else:
            return "not found"
    return each_value_dict


def _getAllKeysOfResponse(dict_obj):
    for key , value in dict_obj.items():
        yield key
        if isinstance(value, dict):
            for k in _getAllKeysOfResponse(value):
                yield k


def getKeys(response_body):
    keyListGlobal = []
    if isinstance(response_body, dict):
      keyListGlobal = list(_getAllKeysOfResponse(response_body))
    elif isinstance(response_body, list):
        for each in response_body:
            keyList = list(_getAllKeysOfResponse(each))
            keyListGlobal = [*keyListGlobal, *keyList]
    
    return list(set(keyListGlobal))
              


def getNestedListData(i, json_data, key_val):
    """parse nested lists in response"""
    # check if response is empty or not, if response is empty, how did it reach here?

    br_start = i.find('[')
    br_end = i.find(']')
    key_num = int(i[br_start + 1:br_end])
    if key_val.lower() == 'legacy' or key_val.lower() == 'response':
        if isinstance(json_data[key_num], list):
            i = i[br_end + 1:]
            json_data = json_data[key_num]
            return getNestedListData(i, json_data, key_val)
        else:
            return key_num, json_data
    else:
        if isinstance(json_data[key_val][key_num], list):
            i = i[br_end + 1:]
            json_data = json_data[key_val][key_num]
            return getNestedListData(i, json_data, key_val)
        else:
            return key_num, json_data


def dispatch_dict():
    dispatch = {
        'to': cf.compareTo,
        'notto': cf.compareNotTo,
        'not to': cf.compareNotTo,
        'not_to': cf.compareNotTo,
        'in': cf.compareIn,
        'notin': cf.compareNotIn,
        'not in': cf.compareNotIn,
        'not_in': cf.compareNotIn,
        'contains': cf.compareContains,
        'not_supported': cf.noOperator,
    }
    return dispatch


def compare(reporter_obj, key, operator, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):

    # operators ----- to, notto, not_to, not to, contains, in, except
    gp = reporter_obj

    dispatch = dispatch_dict()
    if operator in list(dispatch.keys()):
        return dispatch[operator](gp, key, value, key_val_dict, tolerance, isLegacyPresent, isLegacyResponse)
    else:
        return dispatch["not_supported"](gp)
    

