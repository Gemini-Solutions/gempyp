import os

# have to discuss about the default location
DEFAULT_GEMPYP_FOLDER = os.getcwd()
DEBUG = True
THREADS = 8
_VERSION = "1.0.0"

urls = {

    "testcases": "http://ec2-3-108-218-108.ap-south-1.compute.amazonaws.com:8080/testcase",
    "suiteInfo": "http://13.127.133.168:8000/suiteinfo/",
    "suiteExec": "http://ec2-3-108-218-108.ap-south-1.compute.amazonaws.com:8080/suiteexe"

}
