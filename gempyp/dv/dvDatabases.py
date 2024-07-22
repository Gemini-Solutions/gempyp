import importlib
class Databases:
    def __init__(self) -> None:
        pass

    def getConnectionString(self,db):
        database = {"snowflake": {"lib": "snowflake.connector", "conn": "connect"},
                    "mongoDB": {"lib": "pymongo", "conn": "MongoClient"},
                    "mysql":{"lib": "mysql.connector", "conn": "connect"},
                    "postgresql":{"lib": "pg8000", "conn": "connect"}}
        db_import = database[db]
        return db_import["lib"],db_import["conn"]
        
