from libs.Base import Base
from data_compare import data_comp as dc
class Compare(Base):
    def __init__(self, test_id, config_data):
       #testcase specific config can be set here for the object
       #also call the base class __init__ to set base config here
       super(Compare, self).__init__(config_data, test_id)
       self.config_data = config_data
       pass

    def run(self):
       #function for running this testcase
       print(dir())
       print(f"Executing testcase {self.testcase_name}")
       res = dc.worker_process((self.test_id,self.config_data))
       r_val, key_only_in_src, key_only_in_tgt,comm_key, diff_count, match_count = res
       print(f"key only in src {key_only_in_src}")
       print(f"key only in tgt {key_only_in_tgt}")
       print(f"commonkey {comm_key}")
       print(f"diff-count {diff_count}")
       print(f"match_count {match_count}")
       pass

if __name__ == "__main__":
    pass
