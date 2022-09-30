from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""

obj.config = "C:\\Users\\ta.agarwal\\gempyp\\tests\\configTest\\features_suite.xml"
obj.MAIL = "tanya.agarwal@geminisolutions.com"


# main condition is necessary
if __name__ == "__main__":
    obj.runner()
