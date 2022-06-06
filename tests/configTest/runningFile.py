# from distutils.command.config import config
# from gempyp.config.xmlConfig import XmlConfig
# from gempyp.engine.engine import Engine
# import sys

# path1 = sys.argv[1]

# def test():

#    # config = XmlConfig("C:\\Users\\sa.chand\\Desktop\\QA\\gempyp\\tests\\configTest\\sampleTest.xml")
#     config = XmlConfig(path1)
 
    
#     Engine(config)
    

# test()
# Import the library
import argparse
# Create the parser
parser = argparse.ArgumentParser()
# Add an argument
parser.add_argument('-config', type=str, required=True)
# Parse the argument
args = parser.parse_args()
# Print "Hello" + the user input argument

string = args.config