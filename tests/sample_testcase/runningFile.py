from gempyp.gemPyp import Gempyp
import sys
import os


obj = Gempyp()

"""Giving the default config file location  and default mail"""

<<<<<<<<< Temporary merge branch 1
obj.config = "GIT:https://github.com/Gemini-Solutions/gempyp/blob/dev/tests/configTest/Gempyp_Test_suite.xml:dev"
=========
<<<<<<< HEAD
obj.config = "C:\\Users\\an.pandey\\gempyp_test\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
>>>>>>>>> Temporary merge branch 2
obj.MAIL = "8979149361t@gmail.com"
=======
obj.config = "C:\\Users\\ar.mishra\\gempyp\\tests\\configTest\\new_test_suite.xml"
obj.MAIL = "arpit.mishra@geminisolutions.com"
>>>>>>> 188212b1702a147d24dc38389a7f944d67dba7bd


# main condition is necessary
if __name__ == "__main__":
    obj.runner()