from pygem.config.xmlConfig import XmlConfig
from pygem.engine.engine import Engine


def test():
    config = XmlConfig("C:\\gemecosystem\\pygem\\tests\\configTest\\sampleTest.xml")
 
    
    Engine(config)

test()