from distutils.command.config import config
from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine
from runningFile import string

def test():

    #config = XmlConfig("C:\\Users\\sa.chand\\Desktop\\QA\\gempyp\\tests\\configTest\\sampleTest.xml")
    config = XmlConfig(string)
 
    Engine(config)

test()