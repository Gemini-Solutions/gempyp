from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine
import os

def test():

    config = XmlConfig("C:\\gempyp\\tests\\configTest\\sampleTest.xml")

    print(type(config), config, vars(config), dir(config))
    
    Engine(config)

    
if __name__ == "__main__":
    test()