import traceback

class Database():

    def __init__(self, db_type, config_data) -> None:
        try:
            if db_type.lower() == "oracle":
                import data_compare.data.db_oracle as db
            elif db_type.lower() == 'mysql':
                import data_compare.data.db_mysql as db
            elif db_type.lower() == 'sqlite':
                import data_compare.data.db_sqlite as db
            elif db_type.lower() == 'postgre':
                import data.db_postgre as db   
            else:
                print("db_type not found")
                self.db_obj = None
            self.db_obj = db.Database(config_data)
        except Exception:
            self.db_obj = None
            print("Exception in db_wrapper {}".format(traceback.format_exc()))
    
    def get_db_obj(self):
        return self.db_obj
