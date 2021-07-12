import json
import os


class Configurator():
    def __init__(self, suite_file. test_file):
        # get the conf dir from env
        conf_dir = os.getenv('CONF_DIR')
        if os.path.isdir(conf_dir):
            suite_file_path = os.path.join(conf_dir, suite_file)
            test_file_path = os.path.join(conf_dir, test_file)
            if os.path.isfile(suite_file_path):
                if os.path.isfile(test_file_path):
                    self.read_config(suite_file_path, test_file_path) 
                else:
                    print("test file path {} doesnt exist".format(test_file_path))
            else:
                print("Suite file path {} doesn't exist".format(suite_file_path))
        else:
            print("CONF_DIR {} doesnt exist".format(conf_dir))

    def read_json(file_path):
        try:
            with open(file_path) as obj:
               conf_data = json.read(obj)
    def read_config(self, suite_file_path, test_file_path):
       with open(suite_file_path)
