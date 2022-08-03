from gempyp.gemPyp import Gempyp
import sys
import os


obj = Gempyp()

"""Giving the default config file location  and default mail"""

obj.config = "GIT:https://github.com/Gemini-Solutions/gempyp/blob/dev/tests/configTest/Gempyp_Test_suite.xml:dev"
obj.MAIL = "8979149361t@gmail.com"


# main condition is necessary
if __name__ == "__main__":
    print(obj.__dict__)
    obj.runner()