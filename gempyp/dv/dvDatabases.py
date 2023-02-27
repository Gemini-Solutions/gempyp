import importlib
class Databases:
    def __init__(self) -> None:
        pass

    def getConnectionString(self,db):
        database = {"snowflake": {"lib": "snowflake.connector", "conn": "connect"},
                    "microsoft sql server": {"lib": "pyodbc", "conn": "connect"},
                    "mongoDB": {"lib": "pymongo", "conn": "MongoClient"},
                    "oracle": {"lib": "cx_oracle", "conn": "connect"},
                    "mysql":{"lib": "mysql.connector", "conn": "connect"},
                    "postgresql":{"lib": "pg8000", "conn": "connect"}}
        db_import = database[db]
        return db_import["lib"],db_import["conn"]
        
