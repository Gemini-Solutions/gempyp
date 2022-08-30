from gempyp.gemPyp import Gempyp
import sys
import os


obj = Gempyp()

"""Giving the default config file location  and default mail"""

obj.config = "C:\\Users\\ta.agarwal\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
obj.MAIL = "tanya.agarwal@geminisolutions.com"


# main condition is necessary
if __name__ == "__main__":
    obj.runner()