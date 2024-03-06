from gempyp.gemPyp import Gempyp


obj = Gempyp()

"""Giving the default config file location  and default mail"""
obj.config = "C:\\Users\\Tanya.Agarwal\\gempyp_final_dev\\gempyp\\testing.xml"

if __name__ == "__main__":
    obj.runner()
