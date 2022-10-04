from gempyp.gemPyp import Gempyp



obj = Gempyp()

"""Giving the default config file location  and default mail"""
obj.config = "C:/Users/ar.mishra/gempyp/tests/configTest/testXML.xml"
obj.MAIL = "arpit.mishra@geminisolutions.com"



# main condition is necessary
if __name__ == "__main__":
    obj.runner()
