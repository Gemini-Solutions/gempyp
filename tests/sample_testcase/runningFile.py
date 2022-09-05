from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""
obj.config = "C:\\Users\\ar.mishra\gempyp\\tests\configTest\\legacy_test.xml"
obj.MAIL = "arpit.mishra@geminisolutions.com"

<<<<<<< HEAD
obj.config = "C:\\Users\\ta.agarwal\\Desktop\\Gempyp_apis\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
# obj.MAIL = "8979149361t@gmail.com"
=======

obj.config = "C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
obj.MAIL = "8979149361t@gmail.com"
>>>>>>> 4911324e2a2e85be3882128ade84f56dd3fb9f0a


# main condition is necessary
if __name__ == "__main__":
    obj.runner()
