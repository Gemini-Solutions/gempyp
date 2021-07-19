import json

def read_json(file_path):
    try:
        #print(file_path)
        with open(file_path) as fobj:
            res = json.load(fobj)
    except Exception:
        res = None
        print("Exception in read_json for file path {} is {}".format(file_path, traceback.format_exc()))
    return res

