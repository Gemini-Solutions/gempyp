from pygem.config.xmlConfig import XmlConfig


def test():
    config = XmlConfig("/home/sa.taneja/Gemini/pygem/tests/configTest/sampleTest.xml")
    print(config.getSuiteConfig())
    print(config.getTestcaseConfig())

test()


