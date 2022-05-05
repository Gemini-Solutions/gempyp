import os
import sys
import traceback
import common.common_functions as cf
# import validator


class Configurator():
    def __init__(self, args) -> None:
        
        try:
            self.default_json_file = 'def_conf.json'
            if args.config and args.dbfile:
                config_file_path = args.config
                dbfile_file_path = args.dbfile
                if os.path.isfile(config_file_path) and os.path.isfile(dbfile_file_path):
                    config_data = cf.read_json(config_file_path)
                    db_data = cf.read_json(dbfile_file_path)
                    if config_data and db_data:
                        self.config_data = config_data
                        self.db_data = db_data
                    else:
                        self.config_data = None
                        self.db_data = None
                        print("Error reading json file {}, {}".format(config_file_path, dbfile_file_path))
                else:
                    self.config_data = None
                    print("Config file {}, {} does not exists".format(config_file_path, dbfile_file_path))
            else:
                srcqueryfile = args.srcQueryFile
                tgtqueryfile = args.tgtQueryFile
                src_query = args.srcQuery
                tgt_query = args.tgtQuery
                config_issue = False
                if not src_query:
                    if os.path.isfile(srcqueryfile):
                        with open(srcqueryfile) as src:
                            src_query = ' '.join(src.readlines()).strip("\n")
                    else:
                        config_issue = True
                        print("Source query file {} not found".format(srcqueryfile))
                if not tgt_query:
                    if os.path.isfile(tgtqueryfile):
                        with open(tgtqueryfile) as tgt:
                            tgt_query = " ".join(tgt.readlines()).strip("\n")
                    else:
                        config_issue = True
                        print("target query file {} not found".format(tgtqueryfile))
                if not config_issue:
                    self.config_data = {
                        "comparisons":{
                            "1":{
                                "srcDatabase" : args.src,
                                "srcTable" : args.srcTab,
                                "srcSchena" : args.srcSchema,
                                "tgtDatabase" : args.tgtDB,
                                "tgtTable": args.tgtTab,
                                "tgtSchema": args.tgtSchema,
                                "src_query": src_query,
                                "tgt_query": tgt_query,
                                "primary_keys": [x for x in args.primaryKeys.split("--")] 
                            }
                        }
                    }
                else:
                    self.config_data = None
                    print("Source Query file {} or Tgt query file {} not found".format(srcqueryfile, tgtqueryfile))
        except Exception:
            print("Exception occured {}".format(traceback.format_exc()))

    def merge_two_dict(self, x, y):
        z = x.copy()  # starts with s's keys and values
        z.update(y)   # modifies z with y's keys and values
        return z

    def set_config(self):
        """
        Combining and seggrating config provided by user and application default config in this method
        """
        try:
            r_val = 0
            if self.config_data:
                config = self.config_data.copy()
                print("Before setting config {}".format(config))
                def_conf = cf.read_json(self.default_json_file)
                print("def_conf is {}".format(def_conf))
                if def_conf:
                    for comp_id in config["comparisons"]:
                        config["comparisons"][comp_id] = self.merge_two_dict(def_conf,config["comparisons"][comp_id])
                else:
                    print("Default conf not found")
                self.config_data = config
                print("After setting config {}".format(config))
                print("Config set successfully")
            else:
                r_val = 1

        except Exception:
            print("Exception occured in set_config {}".format(traceback.format_exc()))
            r_val = 1
        return r_val
    
    def get_config(self):
        return self.config_data, self.db_data
