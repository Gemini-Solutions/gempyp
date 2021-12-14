import baseConfig
import argparse

class cliConfig(baseConfig):

    #overidden
    def parser(self):
        parsed_values = self._cliParse()
        for attr,value in parsed_values.__dict__.items():
            setattr(self,attr,value)
            


    def _cliParse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-config","--c",dest = "config",help = "the Config file", required=True)
        parser.add_argument("-mail","--m",dest="mail",help="mail to send the report to",required=True)
        parser.add_argument("-mode","--M",dest = "mode",help="to run the testcases in seq or optimized",default="SEQUENCE")
        parsed_values = parser.parse_args()
        return parsed_values