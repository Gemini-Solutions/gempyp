from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""

<<<<<<< HEAD
=======
obj.config = "C:\\Users\\ta.agarwal\\gempyp\\tests\\configTest\\features_suite.xml"
obj.MAIL = "tanya.agarwal@geminisolutions.com"
>>>>>>> 76f641c94febf912f18ce288a2c8c38d26f2020c

obj.config = "C:\\Users\\ta.agarwal\\gempyp\\tests\\configTest\\Flask_APIs_suite.xml"
obj.MAIL = "tanya.agarwal@geminisolutions.com"

# main condition is necessary
if __name__ == "__main__":
    obj.runner()
