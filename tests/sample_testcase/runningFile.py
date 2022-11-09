from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""



obj.config = "C:\\Users\\an.pandey\\downgrading\\gempyp\\tests\\configTest\\feature_suite.xml"
obj.MAIL = "tanya.agarwal@geminisolutions.com"

# main condition is necessary
if __name__ == "__main__":
    obj.runner()
