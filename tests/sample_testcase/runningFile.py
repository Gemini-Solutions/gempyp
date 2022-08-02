from gempyp.gemPyp import Gempyp
import sys
import os


obj = Gempyp()

"""Giving the default config file location  and default mail"""

obj.config = "C:\\Users\\ar.mishra\\gempyp\\tests\\configTest\\new_test_suite.xml"
obj.MAIL = "arpit.mishra@geminisolutions.com"


# main condition is necessary
if __name__ == "__main__":
    obj.runner()