from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine


def test():

    config = XmlConfig("C:\\gemecosystem\\pygem\\tests\\configTest\\sampleTest.xml")

    print(type(config))
    
    Engine(config)

    
if __name__ == "__main__":
    test()