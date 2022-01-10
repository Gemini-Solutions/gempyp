from pygem.config.xmlConfig import XmlConfig
from pygem.engine.engine import Engine


def test():
    config = XmlConfig("/home/sa.taneja/Gemini/pygem/tests/configTest/sampleTest.xml")
    print(config.getSuiteConfig())
    c = config.getTestcaseConfig()
    for i in c:
        print(config.getTestcaseData(i))
    
    Engine(config)

test()