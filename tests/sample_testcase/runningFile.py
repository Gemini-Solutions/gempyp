from gempyp.gemPyp import GemPyp
import sys
import os


obj = GemPyp()

# obj.config = "/home/vatsarpit/Desktop/gempyp/gempyp/tests/configTest/Gempyp_Test_suite.xml"
obj.config = "/home/vatsarpit/Desktop/gempyp/gempyp/tests/configTest/testcases.xml"

obj.MAIL = "arpitmishra@gmail.com"


# main condition is necessary
if __name__ == "__main__":
    print(obj.__dict__)
    obj.runner()