import os
import logging
from typing import Dict
from datetime import datetime, timezone
from itertools import chain
import json
from gempyp.libs.enums.status import status
from gempyp.libs.common import findDuration, dateTimeEncoder


class TemplateData:
    def __init__(self, header="Gemini Report"):
        # initliza the data to be stored as a JSON
        self.REPORTDATA = {"Header": header, "steps": []}

    def newReport(self, projectName: str, testcaseName: str):
        """this method is called in testcaseGenerator and will add the initial data for reports json"""
        metadata = []
        # 1st Column
        column1 = {
            "TESTCASE NAME": testcaseName,
            "SERVICE PROJECT": projectName,
            "DATE OF EXECUTION": {"value": datetime.now(timezone.utc), "type": "date"},
        }
        metadata.append(column1)

        self.REPORTDATA["metaData"] = metadata

    def newRow(self, title: str, description: str, status: status, **kwargs):
        """add the rows in reportdata list
        take the arguments given in addRow method
        """
        step = {"title": title, "description": description, "status": status}

        if not kwargs.get("attachment"):
            kwargs.pop("attachment")

        step.update(kwargs)

        self.REPORTDATA["steps"].append(step)

    # finalize the result. Calculates duration etc.
    def finalizeResult(
        self, begin_time: datetime, end_time: datetime, status_counts: Dict
    ):

        """add second column to reportdata and dump all the data in a single variable """
        # column2
        column2 = {
            "EXECUTION STARTED ON": {"value": begin_time, "type": "datetime"},
            "EXECUTION ENDED ON": {"value": end_time, "type": "datetime"},
            "EXECUTION DURATION": findDuration(begin_time, end_time),
        }

        # column3
        column3 = {k.name: v for k, v in status_counts.items()}
        self.REPORTDATA["metaData"].append(column2)
        self.REPORTDATA["metaData"].append(column3)
        # filters
        self.REPORTDATA["FilterNames"] = self._getFilters()
        filter_values = {}
        filter_values["status"] = [value.name for value in status_counts.keys()]
        self.REPORTDATA["FilterValues"] = filter_values

    def _getFilters(self) -> Dict:
        """
        filter the steps so that all the rows will be displayed only once in report 
        """

        filter_names = list(
            set(chain.from_iterable(step.keys() for step in self.REPORTDATA["steps"]))
        )
        # filter_names.pop("status")
        filter_dict = {name: "Input" for name in filter_names}
        filter_dict["status"] = "Dropdown"

        return filter_dict

    # Converts the data to the JSON
    def _toJSON(self) -> str:
        """
        convert the reportdata dict into jsondata and return it to makeReport method
        currently not in use
        """
        try:
            result_data = json.dumps(self.REPORTDATA, cls=dateTimeEncoder)
            return result_data
        except TypeError as error:
            logging.error("Error occured while serializing the testcase Result Data")
            logging.error(f"Error: {error}")
        except Exception as e:
            logging.error("some Error occured")
            logging.error(f"Error: {e}")
        return "Error"

    def makeReport(self):
        """
        creates the html report and save it in the file
        currently not in use
        """
        # for now do this will change to a better solution
        # TODO
        jsonData = self._toJSON()
        return json.loads(jsonData)

