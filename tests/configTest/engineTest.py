from ast import Suite
from distutils.command.config import config
from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine
import argparse

def argParser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-config','-c',dest='config',type=str, required=False)
    parser.add_argument('-MAIL','-m',dest='MAIL', type=str, required=False)
    parser.add_argument('-PROJECT','-p',dest='PROJECT', type=str, required=False)
    parser.add_argument('-REPORT_NAME','-rn',dest='REPORT_NAME', type=str, required=False)
    parser.add_argument('-MODE','-mode',dest='MODE', type=str, required=False)
    parser.add_argument('-ENV','-env',dest='ENV', type=str, required=False)
    parser.add_argument('-TYPE','-type',dest='-t', type=str, required=False)

    args = parser.parse_args()
    return args


def test():
import os

def test():

    config = XmlConfig("C:\\gempyp\\tests\\configTest\\sampleTest.xml")

    print(type(config))
    
    args = argParser()
    
    xmlPath = "C:\\Users\\sa.chand\\Desktop\\QA\\gempyp\\tests\\configTest\\sampleTest.xml"
    if args.config != None:
        xmlPath = args.config
    config = XmlConfig(xmlPath)
    
    config.cli_config = vars(args)
    config.update()

    Engine(config)

    
if __name__ == "__main__":
    test()