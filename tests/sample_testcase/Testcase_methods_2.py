from gempyp.engine.gempypHelper import Gempyp


class sample2(Gempyp):
    def __init__(self):
        pass 

    def verify(self):
        self.report = Gempyp("Gempyp", "verify_testcase").reporter
        self.report.addRow("test", "desc", self.PASS)
        # for status, we can use self.PASS or Gempyp.PASS
        return self.report

    def Main(self):
        self.report = Gempyp("Gempyp", "Main_testcase").reporter
        self.report.addRow("main test", "main desc", Gempyp.PASS)
        return self.report

    def main(self):
        self.report = Gempyp("Gempyp", "main_Testcase_sample_2").reporter
        self.report.addRow("main test", "main desc", self.PASS)
        return self.report

if __name__ == "__main__":
    sample2().verify()  
     
