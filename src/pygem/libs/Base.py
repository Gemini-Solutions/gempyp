
class Base():
    def __init__(self, config_data, test_id):
        # set up base level config  here
        self.testcase_name = config_data["name"]
        self.testcase_type = config_data["test_type"]
        self.test_id = test_id
        

    def func1(self):
        #functions which can be useful for all type of test case could be written here 
        pass

    def set_conf(self):
       #read and set conf object here
       #reading json or yml or excel function could be written in common file , this method should take of assigning varibale for this class use 
       pass
    def get_conf(self):
       pass
        
