from gempyp.gemPyp import Gempyp
import sys
import os


obj = Gempyp()

"""Giving the default config file location  and default mail"""

<<<<<<< HEAD
obj.config = "C:\\Users\\ta.agarwal\\gempyp\\tests\\configTest\\features_suite.xml"
=======
<<<<<<< HEAD
obj.config = "C:\\Users\\an.pandey\\gempyp_test\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
>>>>>>> 583215ade187e590ca1e7e275a42329eebb7fd92
obj.MAIL = "8979149361t@gmail.com"
=======
obj.config = "C:\\Users\\ar.mishra\\gempyp\\tests\\configTest\\new_test_suite.xml"
obj.MAIL = "arpit.mishra@geminisolutions.com"
>>>>>>> 188212b1702a147d24dc38389a7f944d67dba7bd


# main condition is necessary
if __name__ == "__main__":
    obj.runner()