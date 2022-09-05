from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""
obj.config = "C:\\Users\\ar.mishra\gempyp\\tests\configTest\\legacy_test.xml"
obj.MAIL = "arpit.mishra@geminisolutions.com"


obj.config = "C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
obj.MAIL = "8979149361t@gmail.com"


# main condition is necessary
if __name__ == "__main__":
    obj.runner()
