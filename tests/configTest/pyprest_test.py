from re import X
from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine


def test():

    # config = XmlConfig("/home/vatsarpit/Desktop/gempyp/gempyp/tests/configTest/sampleTest_pyprest.xml")
    # config = XmlConfig("./tests/configTest/features_suite.xml")
    config = XmlConfig("/home/vatsarpit/Desktop/gem_api/gem_apis/gem_apis.xml")

    
    Engine(config)


if __name__ == "__main__":
    
    test()