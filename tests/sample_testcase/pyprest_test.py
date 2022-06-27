from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine


def test():

    config = XmlConfig("C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\features_suite.xml")

    
    Engine(config)


if __name__ == "__main__":
    
    test()