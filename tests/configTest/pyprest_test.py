from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine


def test():

    config = XmlConfig("C:\\Users\\ar.mishra\\gempyp\\tests\\configTest\\sample_test_variables.xml")
    
    Engine(config)


if __name__ == "__main__":
    
    test()