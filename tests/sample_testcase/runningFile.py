from gempyp.gemPyp import GemPyp


obj = GemPyp()

obj.config = "C:\\Users\\ar.mishra\\gempyp\\tests\\configTest\\features_suite.xml"
obj.MAIL = "arpitmishra.sln123@gmail.com"


# main condition is necessary
if __name__ == "__main__":
    obj.runner()