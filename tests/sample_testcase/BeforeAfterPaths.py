import logging
from gempyp.libs.common import importFromPath
import importlib
import sys
import traceback
import os
def Path(filePath):
    import_flag=0
    try:
        logging.info("--------Trying importing modules--------")
        dynamicTestcase = importlib.import_module(filePath)        
        return dynamicTestcase
    except Exception as i:
        logging.info("-------Testcase not imported as module, Trying with absolute path-------")
        try:
            script_path, script_name = importFromPath(filePath)
            script_name = script_name.split(".")[0]
            if script_path is not None:
                sys.path.append(script_path)
            try:
                dynamicTestcase = importlib.import_module(script_name)   
            except Exception:
                logging.info("when absolute and module import both failed")
                try:
                    print(sys.path)
                    lib_path = os.path.join(sys.path[0], script_path)
                    sys.path.append(lib_path)
                    dynamicTestcase = importlib.import_module(script_name.split(".")[0])  
                    import_flag = 1 
                except Exception:
                    traceback.print_exc()
                if import_flag != 1:
                    traceback.print_exc()
            return dynamicTestcase
        except Exception as e:
            logging.error("----- Error occured file could not be imported using any of the methods.-----")
            traceback.print_exc()
            return e








if __name__ == "__main__":
    filePath="gempyp.pyprest.beforeAfterSample"
    Path(filePath).before.before_()