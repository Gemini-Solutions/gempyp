import logging
from typing import Dict
from datetime import datetime, timezone
from itertools import chain
import json
from pygem.libs.enums.status import status
from pygem.libs.common import findDuration, dateTimeEncoder


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
            "DATE OF EXECUTION": datetime.now(timezone.utc),
        }
        metadata.append(column1)

        self.REPORTDATA["MetaData"] = metadata

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
            "EXECUTION STARTED ON": beginTime,
            "EXECUTION ENDED ON": endTime,
            "EXECUTION DURATION": findDuration(beginTime, endTime),
        }

        # column3
        column3 = {k.name: v for k, v in statusCounts.items()}

        self.REPORTDATA["MetaData"].append(column2)
        self.REPORTDATA["MetaData"].append(column3)

        # filters
        self.REPORTDATA["filterNames"] = self._getFilters()
        filterValues = self.REPORTDATA.get("filterValues", {})
        filterValues["status"] = [value.name for value in statusCounts.keys()]

    def _getFilters(self) -> Dict:

        filterNames = list(
            set(chain.from_iterable(step.keys() for step in self.REPORTDATA["steps"]))
        )
        # filterNames.pop("status")
        filterDict = {name: "input" for name in filterNames}
        filterDict["status"] = "multiSelect"

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

    def makeReport(self, Result_Folder):
        """
        creates the html report and save it in the file
        """
        jsonData = self._toJSON()
        # print(jsonData)
        # TODO
        # write the json to a file and make the copy the template to the folder
        Result_File = None
        # return the html file location
        return Result_File
