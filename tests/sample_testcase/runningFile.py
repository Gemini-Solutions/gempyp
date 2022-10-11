from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""



obj.config = "C:\\Users\\ta.agarwal\\Pictures\\gempyp\\tests\\configTest\\Flask_APIs_suite (1).xml"
obj.MAIL = "tanya.agarwal@geminisolutions.com"

# main condition is necessary
if __name__ == "__main__":
    obj.runner()
