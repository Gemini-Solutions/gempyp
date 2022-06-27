import os
import sys
from libs import common 
from data_compare import compare 
import traceback
import argparse

def test():
   print("hello1")

def test2():
   print("hello3")
   return "hello3"

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--suite",help="suite Config File Path")
    parser.add_argument("-tc","--testcase",help="test Config File Path")

    args = parser.parse_args()
    return args

class GemPyp():
     def __init__(self, s_config_data, t_config_data):
         #read the conf here
         #create suite level result dictionary here
         #create test level result dictionary here
         self.suite_conf = s_config_data  # not using this data as of now.
         self.test_conf = t_config_data
         # adding only with execute =Yes 
         self.test_conf = {x : self.test_conf[x] for x in self.test_conf if self.test_conf[x]["execute"].lower() == 'yes'}
         
     
     def execute(self):
         #create a pool of process here
         # create testcase object depending upon type of testcase and call the function run using that object
         
         #update the result for each test case
         #identifying independent task and tasks which have dependency here, create task roster here for executor to run
         
         #running sequentially, update this code with engine logic
         try:
             for test in self.test_conf:
                 test_type = self.test_conf[test]["test_type"].lower()
                 if test_type == "data_comp": 
                     obj = compare.Compare(test, self.test_conf[test])
                     obj.run()
                 else:
                     # dynamicaly load rclass and execute the run function
                     pass
         except Exception: 
            traceback.print_exc()  
     def create_report(self):
         pass

if __name__ == "__main__":
    args = parse_argument()
    if args:
        conf_dir = os.getenv('CONF_DIR')
        s_conf_file_path = os.path.join(conf_dir, args.suite)
        t_conf_file_path = os.path.join(conf_dir, args.testcase)
        if os.path.isfile(s_conf_file_path) and os.path.isfile(t_conf_file_path):
            s_config_data = common.read_json(s_conf_file_path)
            t_config_data = common.read_json(t_conf_file_path)
        else:
            print(f"config file{s_conf_file_path} does not exist")
            sys.exit(1)
        obj = GemPyp(s_config_data, t_config_data)
        obj.execute()
    else:
         print("Argument parsing had issues")
