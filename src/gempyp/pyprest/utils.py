import json
import ast
import re


def format_resp_body(response_body):
    if not isinstance(response_body, list):
        try:
            formatted_response_body = json.loads(response_body.decode("utf-8"))
            print("keycheck ----- 1")
        except Exception:
            try:
                formatted_response_body = json.loads(ast.literal_eval(response_body.decode("utf-8")))
                print("keycheck ----- 2")
            except Exception:
                try: 
                    formatted_response_body = json.loads(str(response_body.encode("utf-8")))
                    if "b'" in formatted_response_body:
                        formatted_response_body = formatted_response_body.strip("b'").strip("'")
                    print("keycheck ----- 3")
                except Exception:
                    try:
                        formatted_response_body = json.loads(response_body)
                    except Exception as e:
                        formatted_response_body = response_body

    else:
        formatted_response_body = response_body
    return formatted_response_body


def fetch_value_of_key(json_, key_partition_list, key_search_result, final_key_value={}):
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
                if key_val != "response":
                    json_ = json_[key_val]
                for each_value in json:
                    index_of_key = key_partition_list.index(key)
                    value_returned = get_values_for_each(each_value, key_partition_list[index_of_key + 1:])
                    each_value_list.append(value_returned)
                del key_partition_list[index_of_key + 1:]
                flag = 1
            elif re.match(regex_int, key):
                br_start = key.find('[')
                br_end = key.find(']')
                key_val = key[:br_start]
                key_num = int(key[br_start + 1:br_end])
                if key_val == "response" and isinstance(json_, list):
                    json_ = json_[key_num]
                else:
                    json_ = json_[key_val][key_num]
            else:
                if isinstance(json_, str) and json_ != "":
                    json_ = json.dumps(json_)
                if json_ != "":
                    json_ = json_[key]
                if json_ is None:
                    json_ = "null"
        if flag != 1:
            final_key_value[actual_key] = json_
        else:
            final_key_value[actual_key] = each_value_list
        
        return final_key_value
   
def get_values_for_each(each_value_dict, keys_to_fetch):
    for key in keys_to_fetch():
        if key in each_value_dict:
            each_value_dict = each_value_dict[key]
            if each_value_dict is None:
                each_value_dict = "null"
                break
        else:
            return "not found"
    return each_value_dict