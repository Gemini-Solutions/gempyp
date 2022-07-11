from gempyp.gemPyp import Gempyp
import sys
import os


obj = Gempyp()

"""Giving the default config file location  and default mail"""

obj.config = "C:\\Users\\sa.chand\\Desktop\\gemEcosystem\\gempyp\\tests\\configTest\\Gempyp_Test_suite.xml"
obj.MAIL = "ankitapandey281999@gmail.com"


# main condition is necessary
if __name__ == "__main__":
    print(obj.__dict__)
    obj.runner()