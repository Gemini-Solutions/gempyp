import os
import sys
import datetime
import time

class Comparator():

    def __init__(self, config, src_data, tgt_data, src_header, tgt_header) -> None:
        if config["comp_type"].lower() =="python":
            import data_compare.core.python_obj_comparator as poc
            self.comp_obj = poc.ObjComparator(src_data, tgt_data, config["primary_keys"], config["tolerance"], src_header, tgt_header )
        elif config["comp_type"].lower() =='pandas':
            print("not impemented yet")
    
    def compare(self):
        return self.comp_obj.startCompare()
