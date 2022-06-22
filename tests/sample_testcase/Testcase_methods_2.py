from gempyp.engine.simpleTestcase import AbstractSimpleTestcase


class sample2(AbstractSimpleTestcase):
    def __init__(self):
        pass 

    def verify(self, reporter):
        reporter.addRow("test", "desc", self.Status.PASS)
        reporter.logger.info("We are testing logger inside verify method")
        return reporter

    def Main(self, reporter):
        reporter.addRow("main test", "main desc", self.Status.PASS)
        reporter.logger.info("We are testing logger inside main method")
        return reporter

    def main(self, reporter):
        reporter.addRow("main test", "main desc", self.Status.PASS)
        return reporter

if __name__ == "__main__":
    sample2().verify()  
     
