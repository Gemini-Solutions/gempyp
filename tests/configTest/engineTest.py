from pygem.config.xmlConfig import XmlConfig
from pygem.engine.engine import Engine


def test():
    config = XmlConfig("/home/sa.taneja/Gemini/pygem/tests/configTest/sampleTest.xml")
 
    
    Engine(config)

test()