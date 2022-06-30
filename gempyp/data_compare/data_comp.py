import argparse
import os
import sys
import traceback
import datetime
import uuid
# from logger import logger
#from configurator import configurator,validator
from data_compare.data import database,data
from data_compare.core import comparator
from multiprocessing import Pool, Process


class DVM():
    """Usinf this class only for web based request , will merge it with ain later on"""
    def __init__(self, config_data):
        self.config_data = config_data
    def set_config(self):
        pass
    def validate_config(self):
        pass
    def get_src_data(self):
        pass
    def get_tgt_data(self):
        pass
    def get_metadata_db_connection(self):
        pass
    def close_metadata_db_connection(self):
        pass
    def get_results(self):
        try:
            res_dict = {}
            #selecting only execute = yes comparison
            config_list = [(uuid.uuid4(),self.config_data)]
            if config_list:
                process_no = len(config_list)
                pool = Pool(processes=process_no)
                for res in pool.imap_unordered(worker_process,config_list):
                    res = list(res)
                    if res[0] == 0:
                        res_dict["status"]='PASS'
                        r_val,key_only_in_src,key_only_in_tgt,common_keys,diff_count,match_count = [res[i] for i in (0, 1, 2, 3, 4, 5)]
                        res_dict["comp_status"] = "FAIL"
                        if diff_count==0 and len(key_only_in_src)==0 and len(key_only_in_tgt)==0:
                            print("Comparison passed for comp_id {}".format(res[1]))
                            res_dict["comp_status"] = "PASS"
                            res_dict["match_count"] = match_count
                        elif diff_count>0:
                            print("Diff found {}".format(diff_count))
                            res_dict["diff"]=diff_count
                            res_dict["match_count"] = match_count
                        elif len(key_only_in_src)>0:
                            print("Extra key found in src {}".format(len(key_only_in_src)))
                            res_dict['key_only_in_src']=len(key_only_in_src)
                        elif len(key_only_in_tgt)>0:
                            print("Extra key found in tgt {}".format(len(key_only_in_tgt)))
                            res_dict['key_only_in_tgt']=len(key_only_in_tgt)
                    else:
                        res_dict["status"] = "FAIL"
                        print("Comparison failed for comp_id {} ".format(res[1]))
            else:
                print("No executable test case found")
            print("Exiting from get_results")
        except Exception:
            print("Exception in get_results {}".format(traceback.format_exc()))
        return res_dict    



def parseCmdLine():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c","--config",help="Config File Path")
        parser.add_argument("-db", "--dbfile", help="Database File")
        parser.add_argument("-sdb","--srcDB",help="Source Database Name")
        parser.add_argument("-st","--srcTab",help="Source Table")
        parser.add_argument("-ss","--srcSchema",help="Source Schema")
        parser.add_argument("-tdb","--tgtDB",help="Target Database")
        parser.add_argument("-tt","--tgtTab",help="target Table")
        parser.add_argument("-ts","--tgtSchema",help="target schema")
        parser.add_argument("-sq","--srcQuery",help="Source Query")
        parser.add_argument("-tq","--tgtQuery",help="Target Query")
        parser.add_argument("-sqf","--srcQueryFile",help="Path of source query file")
        parser.add_argument("-tqf","--tgtQueryFile",help="Path of target query file")
        parser.add_argument("-pk","--primaryKeys",help="primary key list separated with double hyphen(--)")
        args = parser.parse_args()
    except Exception:
        args = None
        print("Exception occured in parseCmdLine {}".format(traceback.format_exc()))
    return args


        
def checkCmdLineParams(args): 
    try:
        r_val = 1
        if args.config and args.dbfile:
            r_val = 0
        else:
            print("Config file or DB file not passed checking commandline variable")
            paramMissing =False
            if not args.srcDB:
                print("SrcDB not passed. Exiting")
                paramMissing = True
            if not args.tgtDB:
                print("tgtDB not passed. Exiting")
                paramMissing = True
            if not args.srcQueryFile:
                print("srcQueryFile is not passed.checking for srcQuery")
                if not args.srcQuery:
                    paramMissing = True
                    print("srcQuery is also not found .exiting")
            if not args.tgtQueryFile:
                print("tgtQueryFIle is not passed . checking for tgtQuery")
                if not args.tgtQuery:
                    paramMissing = True
                    print('tgtQuery is also passed.exiting')
            if not args.primaryKeys:
                paramMissing = True
                print("primaryKeys not passed.exiting")
            if not paramMissing:
                r_val = 0
        if r_val ==0 :
            print("Check cmd line passed")
    except Exception:
        print("Exception in checkCmdLineParam {}".format(traceback.format_exc()))
    return r_val


def worker_process(config):
    try:
        print(f"config is {config}")
        r_val = 1
        comp_id = config[0]
        print(config[0])
        print("Worker process for cmp_id {} started".format(comp_id))
        comp_info = config[1]
        print(comp_info)
        DataObj = data.Data(comp_info)
        src_data,src_header,tgt_data,tgt_header = DataObj.get_data()
        if src_data and tgt_data:
            #creating comparator object
            comp_obj = comparator.Comparator(comp_info, src_data, tgt_data, src_header, tgt_header)
            res = comp_obj.compare()
        else:
            print("No data found either in src or in tgt. Not Comparing")
            res = (1, None, None, None, None, None)
        print("Worker process running for comp_id {} completed".format(comp_id))
    except Exception:
        print("Exception in worker proces {}".format(traceback.format_exc()))
        res = (1, None, None, None, None, None)
    return res

def main():
    try:
        print("inside main")
        r_val = 1
        args = parseCmdLine()
        r_val = checkCmdLineParams(args)
        if r_val == 0:
            configuratorObj = configurator.Configurator(args)
            r_val = configuratorObj.set_config()
            if r_val == 0:
                config_data, db_data = configuratorObj.get_config()
                print("Config data in main is {}".format(config_data))
                print("DB data in main is {}".format(db_data))
                res_list = []
                #selecting only execute = yes comparison
                config_list = [[x,config_data['comparisons'][x]] for x in config_data["comparisons"] if config_data['comparisons'][x]['execute'].lower()=='yes']	
                print("config_list af is {}".format(config_list))
                for i in config_list:
                    db_src = i[1]['srcDatabase']
                    db_tgt = i[1]['tgtDatabase']
                    db_one = {}
                    db_two = {}
                    for j in db_data[db_src]:
                    #print(i)
                        db_one['src_'+j]=db_data[db_src][j]
                    for j in db_data[db_tgt]:
                        db_two['tgt_'+j]=db_data[db_tgt][j]
                #print("db_src is {}".format(db_one))
                #print("db_tgt is {}".format(db_two)) 
                    i[1] = {**i[1], **db_one, **db_two}
                print("config_list is {}".format(config_list))
                if config_list:
                    process_no = max(len(config_list),2) #taking it 2 for local machine will increase later
                    
                    if process_no>1:
                        pool = Pool(processes = process_no)
                        for res in pool.imap_unordered(worker_process,config_list):
                            res = list(res)
                            print(res)
                            #print(res)
                            if res[0]==0:
                                r_val,key_only_in_src, key_only_in_tgt, common_keys, diff_count, match_count = [res[i] for i in (0, 1, 2, 3, 4, 5)]
                                if diff_count==0 and len(key_only_in_src)==0 and len(key_only_in_tgt)==0:
                                    print("Comparison passed for comp_id {}".format(res[1]))
                                elif diff_count>0:
                                    print("Diff found {}".format(diff_count))
                                elif len(key_only_in_src)>0:
                                    print("Extra key found in src {}".format(key_only_in_src))
                                elif len(key_only_in_tgt)>0:
                                    print("Extra key found in tgt {}".format(key_only_in_tgt))
                            else:
                                print("Comparison failed for comp_id {}".format(res[1]))
                    elif 2==3:
                        #this code is not used
                        #launching a single process for single comparisons
                        proc = Process(target = worker_process, args = config_list)
                        proc.start()
                        proc.join()
                    else:
                        res = worker_process(config_list[0])
                        if res[0]==0:
                                r_val,key_only_in_src, key_only_in_tgt, common_keys, diff_count, match_count = [res[i] for i in (0, 1, 2, 3, 4, 5)]
                                if diff_count==0 and len(key_only_in_src)==0 and len(key_only_in_tgt)==0:
                                    print("Comparison passed for comp_id {}".format(res[1]))
                                elif diff_count>0:
                                    print("Diff found {}".format(diff_count))
                                elif len(key_only_in_src)>0:
                                    print("Extra key found in src {}".format(key_only_in_src))
                                elif len(key_only_in_tgt)>0:
                                    print("Extra key found in tgt {}".format(key_only_in_tgt))
                        else:
                            print("Comparison failed for comp_id {}".format(res[1]))
                else:
                    print("No executable testcase found")
                r_val = 0
    except Exception:
        print("Exception in main {}".format(traceback.format_exc()))

if __name__ == '__main__':
    print("hello world")
    main()
