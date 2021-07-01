import sys
import os
import json
import traceback
import pandas as pd
import time
from cryptography.fernet import Fernet
import warnings
from getpass import getpass, getuser

KEY_DIR = (
    	os.path.abspath('/home/tanvi/Downloads/PygemDump/')
)

def read_json(file_path):
    try:
        #print(file_path)
        with open(file_path) as fobj:
            res = json.load(fobj)
    except Exception:
        res = None
        print("Exception in read_json for file path {} is {}".format(file_path, traceback.format_exc()))
    return res

def write_json(data, file_path):
    try:
        r_val = 1
        with open(file_path,'w') as fobj:
            json.dump(data, fobj, indent=4, sort_keys=True)
        r_val = 0
    except Exception :
        print("Exception in write json for file_path {} is {} ".format(file_path, traceback.format_exc()))
    return r_val

def mem_usage(pandas_obj):
    if isinstance(pandas_obj, pd.DataFrame):
        usage_b = pandas_obj.memory_usage(deep=True).sum()
    else:  # we assume if it is not a df it is a series
        usage_b = pandas_obj.memory_usage(deep= True)
    usage_mb = usage_b / 1024 ** 2  #converting bytes to megabytes
    return "{:03.2f}".format(usage_mb)

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print("{} {} seconds".format(method.__name__, (te-ts)))
        return result
    return timed

def exc_handler(method):
    def check_exc(*args, **kw):
        try:
            res = method(*args, **kw)
        except Exception:
            res = None
            print("Exception occured in {} as {}".format(method.__name__, traceback.format_exc()))
        return res
    return check_exc

def decrypt(enc_pass):
    cur_user = getuser()
    key_file_name = "." + cur_user + ".key"
    key_file_path = os.path.join(KEY_DIR, key_file_name)
    print("keyfile path is {}".format(key_file_path))
    if not os.path.exists(key_file_path):
        print(
            "Keyfile does not exist. Exiting"
        )
        sys.exit(1)
    else:
        print("Keyfile exists. Retrieving key")
        with open(key_file_path) as f:
            key = f.readline()
    try:
        f = Fernet(key)
        pass
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            enc_pass = enc_pass.encode('utf-8')
            dec_passwd = f.decrypt(enc_pass)
            dec_passwd = dec_passwd.decode('utf-8')
    except Exception:
        dec_passwd = None
        traceback.print_exc()
    return dec_passwd
    
if __name__ == '__main__':
    pass





