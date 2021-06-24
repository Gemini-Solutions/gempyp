import os
import sys
from datetime import date, datetime
import traceback
import decimal
# import cdecimal
import multiprocessing
# import Sybase
import pdb

DVM_NUMERIC_TYPES = [float, int, decimal.Decimal]
DVM_STR_TYPES = [str,bytearray]
DVM_DATETIME_TYPES = [datetime,datetime.time,datetime.date]
DVM_BOOL_TYPES = [bool]
#will add seconds and millis econs to this later
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M"

class ObjComparator():
    def __init__(self, src_data, tgt_data, keys, tolerance, src_header, tgt_header):
        self.src_data = src_data
        self.tgt_data = tgt_data
        print("Len of src_data {}".format(len(src_data)))
        print("Len of tgt_data {}".format(len(tgt_data)))
        print(src_data)
        print(tgt_data)
        self.keys = [x.lower() for x in keys]
        self.tolerance = tolerance
        self.src_header = src_header
        self.tgt_header = tgt_header
        #supposing the order of column in both src and target is same
        #to do - in pre processor, arranging the column from both src and tgt in same order without fetching data
        #then re running the query to create result set in ordered column fashion this is the case for select * query 
        #if user is providing the columns, they should order the columns similary on bothe src and tgt side
        self.src_key_idx = [idx for idx,item in enumerate(self.src_header) if item in self.keys]
        self.tgt_key_idx = [idx for idx,item in enumerate(self.tgt_header) if item in self.keys]
        self.src_val_idx = [idx for idx,item in enumerate(self.src_header) if item not in self.keys]
        self.tgt_val_idx = [idx for idx,item in enumerate(self.tgt_header) if item not in self.keys]
    
    def convert_to_dict(self):
        try:
            self.src_dict = {tuple([item[i] for i in self.src_key_idx ]):tuple([item[i] for i in self.src_val_idx]) for item in self.src_data }
            #need to add a check whether user inputted index column have duplicate value or not , i.e index value are really unique or not
            self.tgt_dict = {tuple([item[i] for i in self.tgt_key_idx ]):tuple([item[i] for i in self.tgt_val_idx]) for item in self.tgt_data }
        except Exception :
            print("Exception in convert to dict {}".format(traceback.format_exc()))

    def startCompare(self):
        try:
            r_val = 1
            print("Start compare at {}".format(datetime.now()))
            self.convert_to_dict()
            self.set_src_keys = set(self.src_dict.keys())
            self.set_tgt_keys = set(self.tgt_dict.keys())
            self.key_only_in_src = list(self.set_src_keys - self.set_tgt_keys)
            self.key_only_in_tgt = list(self.set_tgt_keys - self.set_src_keys)
            self.common_keys = list(self.set_tgt_keys.intersection(self.set_src_keys))
            print("key only in src {}".format(len(self.key_only_in_src)))
            print("key only in tgt {}".format(len(self.key_only_in_tgt)))
            print("common_keys {}".format(len(self.common_keys)))
            diff_count,match_count = compare(self.src_dict, self.tgt_dict, self.common_keys,self.tolerance)
            print("diffcount {}, match_count {}".format(diff_count,match_count))
            if diff_count == 0:
                r_val = 0
            else:
                r_val = diff_count
            res = (r_val, self.key_only_in_src, self.key_only_in_tgt, self.common_keys, diff_count, match_count)
            #print('res', res)
            print("Ended comparison at {}".format(datetime.now()))
        except Exception:
            print("Exception in startCompare {}".format(traceback.format_exc()))
            res = (1, None, None, None, None, None)
        return res


def isclose(a, b, rel_tol=1e-06, abs_tol = 0.0):
    """
    a and b : are the two values to be tested to relative closeness
    rel_tol: is the relatice tolerance -- it is the amount of error allowed, relative to the larger absolute value of a or b
    for example, to set a tolerance of 5%, pass tole=0.05 . the default tolerance is 1e-06
    whic assures that the two values are same within about 9 decimal digits. rel_tol must be greater than 0.0
    abs_tol = is a minimum absolute tolerance level--usefull for comaprison near zero
    """
    if type(rel_tol)!=float:
        try:
            rel_tol = float(rel_tol)
        except Exception:
            rel_tol = 1e-06
    return abs(a-b)<=max(rel_tol*max(abs(a),max(b),abs_tol))

def compare(srcdict, tgtdict, keys, tolerance, proc_queue=None, type_check = False, resType = 'basic'):
    """
    resType :(binary or basic or advance)
            binary result would be just pass/fail without diff inofrmation
            basic: result be put in json with diff information
            advance: complete report in excel
    """
    try:
        print(srcdict)
        print(tgtdict)
        match_count = 0
        diff_count = 0
        for key in keys:
            #matching the column at once, if they match we would do nothing, if they dont we will be matching column by column
            if srcdict[key] == tgtdict[key]:
                print("all values matched")
                match_count = match_count +len(srcdict[key])
            else:
                #now compare values one by one
                if len(srcdict[key]) == len(tgtdict[key]):
                    for val in range(len(srcdict[key])):
                        src_val = srcdict[key][val]
                        tgt_val = tgtdict[key][val]
                        src_type = type(src_val)
                        tgt_type = type(tgt_val)
                        #directly checking if the value matches or not
                        if src_val == tgt_val:
                            print("direct value matched")
                            match_count+=1
                            #val is same no diff
                        elif src_val is None or tgt_val is None:
                            diff_count+=1
                            #any one val is None so there is a diff
                        else:
                            #comparing string types
                            if src_type in DVM_STR_TYPES and tgt_type in DVM_STR_TYPES:
                                #str vs unicode is matched without issue
                                #str vs bytearray is matching without issue
                                #but bytearray vs unicode, we need to convert them to str
                                print("checking str type")
                                if src_type in [bytearray]:
                                    src_val = str(src_val)
                                if tgt_type in [bytearray]:
                                    tgt_val = str(tgt_val)
                                if src_val==tgt_val:
                                    match_count+=1
                                else:
                                    diff_count+=1
                            #matching numeric types:
                            elif src_type in DVM_NUMERIC_TYPES and tgt_type in DVM_NUMERIC_TYPES:
                                print("checking numeric type")
                                #only check for tolerance when type is either float or decimal.Decimal
                                if src_type in (float,decimal.Decimal) and tgt_type in (float,decimal.Decimal):
                                    #isclose only check toelrance for float value not for decimal as we will be converting every other type to float for tolerance comparisons
                                    if isclose(src_val,tgt_val,tolerance):
                                        match_count+=1
                                    else:
                                        diff_count+=1
                                else:
                                    #the number must be integer hcecking directly
                                    if src_val == tgt_val:
                                        match_count+=1
                                    else:
                                        diff_count+=1

                            #comparig datetime object
                            elif src_type in DVM_DATETIME_TYPES and tgt_type in DVM_DATETIME_TYPES:
                                print("checking datetime type")
                                if src_type ==datetime.date:
                                    src_val = datetime.combine(src_val,datetime.min.time())
                                if tgt_type==datetime.date:
                                    tgt_val = datetime.combine(tgt_val,datetime.min.time())
                                if src_val == tgt_val:
                                    match_count+=1
                                else:
                                    diff_count+=1
                            
                            #comparing bool type
                            elif src_type in DVM_BOOL_TYPES and tgt_type in DVM_BOOL_TYPES:
                                if src_val==tgt_val:
                                    match_count+=1
                                else:
                                    diff_count+=1
                            else:
                                diff_count+1
                                print("src {} and tgt type {} unidentified".format(src_type, tgt_type))
                
                if resType.lower() == 'binary':
                    #to do later
                    pass
  
        if proc_queue:
            proc_queue.put([diff_count, match_count])
        else:
            print("returning from try")
            return diff_count, match_count

    except Exception:
        print("Exception in compare method {}".format(traceback.format_exc()))
        if proc_queue:
            proc_queue.put([None, None])
        else:
            print("returnig from except")
            return None, None


if __name__ == "__main__":
    pass
