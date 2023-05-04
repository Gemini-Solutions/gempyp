from gempyp.gemPyp import Gempyp


obj = Gempyp()

"""Giving the default config file location  and default mail"""
obj.config = ""

if __name__ == "__main__":
    obj.runner()
