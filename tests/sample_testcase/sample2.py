from gempyp.engine.gempypHelper import Gempyp
from gempyp.libs.enums.status import status


class sample2(Gempyp):
    def __init__(self):
        self.report = Gempyp("Gempyp", "testing").reporter  

    def verify(self):
        # self.report = Gempyp("Gempyp", "testing").reporter
        print("~~~~~~~~~~~~", dir(Gempyp))
        self.report.addRow("test", "desc", status.PASS)
        return self.report

    def Main(self):
        self.report.addRow("main test", "main desc", status.PASS)
        return self.report

if __name__ == "__main__":
    sample2().verify()  
     
