from gempyp.config.xmlConfig import XmlConfig


def test():
    config = XmlConfig("/home/sa.taneja/Gemini/gempyp/tests/configTest/sampleTest.xml")
    print(config.getSuiteConfig())
    print(config.getTestcaseConfig())

test()


