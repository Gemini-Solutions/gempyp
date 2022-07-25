import logging as logger
import json
from gempyp.libs.enums.status import status



class legacyApiComparison:
    def __init__(self,pyprest_obj):
        self.pyprest_obj = pyprest_obj
        self.legacy_api_response = self.pyprest_obj.__dict__["legacy_res"]
        self.current_api_response = self.pyprest_obj.__dict__["res_obj"]

        print("Inside legacy api comparison")

    def responseComparison(self):
        current_status_code = self.current_api_response.status_code
        legacy_status_code = self.legacy_api_response.status_code
        legacy_response_body = json.loads(self.legacy_api_response.response_body)
        current_response_body = json.loads(self.current_api_response.response_body)
 

        if current_status_code == legacy_status_code:
            self.pyprest_obj.reporter.addRow("Comparing Response status code", "Response Codes are equal",
                             status.PASS, 
                             CURRENT_API = f"<b>CURRENT RESPONSE CODE:</b> {current_status_code}" 
                             ,LEGACY_API = f"<b>LEGACY RESPONSE CODE:</b> {legacy_status_code}"
                             )
            # if isinstance(current_response_body, list) and isinstance(legacy_response_body, list):
            #     self.pyprest_obj.reporter.addRow("Comparing Response Types of both response bodies", "Both are list of response(s).",
            #                  status.PASS, LEGACY_API = f"<b>LEGACY RESPONSE BODY:</b> {str(legacy_response_body)}",
            #                  CURRENT_API = f"<b>CURRENT RESPONSE BODY:</b> {str(current_response_body)}" 
            #                  )
            #     if len(current_response_body) == len(legacy_response_body):
            #         self.pyprest_obj.reporter.addRow("Comparing number of elements in both response bodies", "Both of responses having same number of elements",
            #             status.PASS, LEGACY_API = f"<b>TOTAL ELEMENTS IN LEGACY RESPONSE BODY:</b> {len(legacy_response_body)}",
            #             CURRENT_API =f"<b>TOTAL ELEMENTS IN CURRENT RESPONSE BODY:</b> {len(current_response_body)}" 
            #             )
            #     else:
            #         self.pyprest_obj.reporter.addRow("Comparing number of elements in both response bodies", "Both of responses are not having same number of elements",
            #             status.FAIL, LEGACY_API = f"<b>TOTAL ELEMENTS IN LEGACY RESPONSE BODY:</b> {len(legacy_response_body)}",
            #             CURRENT_API = f"<b>TOTAL ELEMENTS IN CURRENT RESPONSE BODY:</b> {len(current_response_body)}" 
            #             )

            # elif isinstance(current_response_body, dict) and isinstance(legacy_response_body, dict):
            #     self.pyprest_obj.reporter.addRow("Comparing Response Types of both response bodies", "Both are JSON response",
            #                  status.PASS, LEGACY_API = f"<b>LEGACY RESPONSE BODY:</b> {str(legacy_response_body)}",
            #                  CURRENT_API = f"<b>CURRENT RESPONSE BODY:</b> {str(current_response_body)}" 
            #                  )
            # else:
            #     self.pyprest_obj.reporter.addRow("Comparing Response Types of both response bodies", "Both response(s) are not of same type.",
            #                  status.PASS, LEGACY_API = f"<b>LEGACY RESPONSE BODY:</b> {str(legacy_response_body)}",
            #                  CURRENT_API = f"<b>CURRENT RESPONSE BODY:</b> {str(current_response_body)}" 
            #                  )
            #     self.pyprest_obj.reporter._miscData["REASON_OF_FAILURE"] += "Both response(s) are not of same type., "
            #     raise Exception("abort")

        else:
            self.pyprest_obj.reporter.addRow("Comparing Response status code", "Response Codes are not equal",
                             status.FAIL, 
                             CURRENT_API = f"<b>CURRENT RESPONSE CODE: {self.current_api_response.status_code}</b>" 
                             ,LEGACY_API = f"<b>LEGACY RESPONSE CODE: {self.legacy_api_response.status_code}</b>"
                             )
            self.pyprest_obj.reporter._miscData["REASON_OF_FAILURE"] += "Both Status codes are not same, "
            # self.logger.info("status code of legacy and current api is not same, aborting testcase.....")
            # raise Exception("abort")


