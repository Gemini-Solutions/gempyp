import logging
from gempyp.reporter.reportGenerator import TemplateData
from gempyp.libs.enums.status import status
class GPLogger(logging.getLoggerClass()):
    def __init__(self, name, level=0):
        super(GPLogger, self).__init__(name, level=level)
        self.template_data = TemplateData()
        self.template_data.newRow(
            "Additional details of testcases", name,status.INFO , attachment=None
        )