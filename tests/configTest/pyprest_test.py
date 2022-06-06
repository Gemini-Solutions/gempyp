from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine


def test():

    config = XmlConfig("C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\sampleTest_pyprest.xml")
    
    Engine(config)


if __name__ == "__main__":
    
    test()