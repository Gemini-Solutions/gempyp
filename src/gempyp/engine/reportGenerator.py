import os
import logging
from typing import Dict
from datetime import datetime, timezone
from itertools import chain
import json
from gempyp.libs.enums.status import status
from gempyp.libs.common import findDuration, dateTimeEncoder


class templateData:
    def __init__(self, header="Gemini Report"):
        # initliza the data to be stored as a JSON
        self.REPORTDATA = {"Header": header, "steps": []}

    def newReport(self, projectName: str, tescaseName: str):
        metadata = []
        # 1st Column
        column1 = {
            "TESTCASE NAME": tescaseName,
            "SERVICE PROJECT": projectName,
            "DATE OF EXECUTION": {"value": datetime.now(timezone.utc), "type": "date"},
        }
        metadata.append(column1)

        self.REPORTDATA["metaData"] = metadata

    def newRow(self, title: str, description: str, status: status, **kwargs):
        step = {"title": title, "description": description, "status": status}

        if not kwargs.get("attachment"):
            kwargs.pop("attachment")

        step.update(kwargs)

        self.REPORTDATA["steps"].append(step)

    # finalize the result. Calulates duration etc.
    def finalizeResult(
        self, beginTime: datetime, endTime: datetime, statusCounts: Dict
    ):
        # column2
        column2 = {
            "EXECUTION STARTED ON": {"value": beginTime, "type": "datetime"},
            "EXECUTION ENDED ON": {"value": endTime, "type": "datetime"},
            "EXECUTION DURATION": findDuration(beginTime, endTime),
        }

        # column3
        column3 = {k.name: v for k, v in statusCounts.items()}

        self.REPORTDATA["metaData"].append(column2)
        self.REPORTDATA["metaData"].append(column3)
        # print("----------- steps", self.REPORTDATA["steps"])
        # filters
        self.REPORTDATA["FilterNames"] = self._getFilters()
        filterValues = {}
        filterValues["status"] = [value.name for value in statusCounts.keys()]
        self.REPORTDATA["FilterValues"] = filterValues

    def _getFilters(self) -> Dict:

        filterNames = list(
            set(chain.from_iterable(step.keys() for step in self.REPORTDATA["steps"]))
        )
        # filterNames.pop("status")
        filterDict = {name: "Input" for name in filterNames}
        filterDict["status"] = "Dropdown"

        return filterDict

    # Converts the data to the JSON
    def _toJSON(self) -> str:
        try:
            ResultData = json.dumps(self.REPORTDATA, cls=dateTimeEncoder)

            return ResultData
        except TypeError as error:
            logging.error("Error occured while serializing the testcase Result Data")
            logging.error(f"Error: {error}")
        except Exception as e:
            logging.error("some Error occured")
            logging.error(f"Error: {e}")
        return "Error"

    def makeReport(self, Result_Folder, name):
        """
        creates the html report and save it in the file
        """
        # for now do this will change to a better solution
        # TODO
        Result_data = ""
        index_path = os.path.dirname(__file__)
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            Result_data = f.read()
        jsonData = self._toJSON()
        return json.loads(jsonData)

