from gempyp.libs.enums.status import status

import json

import random

class beforeAfter:

    def before_method(self,obj):

        obj.pg.addRow("Modifying Request Method","Modified Request Method while in a Before Method<br><b>Request METHOD: </b>GET",status.INFO)

        obj.request.method="GET"

        return obj

    def after_response_code(self,obj):

        if obj.legacy_req is not None and obj.legacy_req.api is not None:

            if(obj.response.status_code==200 and obj.legacy_res.status_code==201):

                obj.pg.addRow("Validating Response Code with Expected Status Codes", "Both status codes are matching with expected status codes while in After Method",

                                status.PASS,

                                 CURRENT_API= "Status code is matching with expected status code for current api", 

                                 LEGACY_API= "Status code is matching with expected status code for legacy api"

                                 )

            else:

                obj.pg.addRow("Validating Response Code with Expected Status Codes", "Both status codes are not matching with expected status codes while in After Method",

                                status.FAIL,

                                 CURRENT_API= "Status code is not matching with expected status code for current api", 

                                 LEGACY_API= "Status code is not matching with expected status code for legacy api"

                                 )

        else:

            if(obj.response.status_code==200):

                obj.pg.addRow("Validating Response Code with Expected Status Codes", "Status code is matching with expected status code wile in After Method",

                                status.PASS

                                 )

            else:

                obj.pg.addRow("Validating Response Code with Expected Status Codes", "Status code is not matching with expected status code while in After Method",

                                status.FAIL

                                 )

        return obj

    def before_body(self,obj):

        email=random.random()

        obj.pg.addRow("Modifying Request Body","Modified Body while in Before Method<br><b>Request Body: </b> {\"name\": \" JOhn\",\"email\": f\"JOhn{email}@gmail.biz\",\"gender\": \"male\",\"status\": \"inactive\"}",status.INFO)

        obj.request.body={        

                "name": " JOhn",

                "email": f"JOhn{email}@gmail.biz",

                "gender": "male",

                "status": "inactive"

            }

        obj.pg.addRow("Modifying Request Headers","Modified Request Headers while in Before Method<br><b>Request Headers: </b>{\"content-type\":\"application/json\",\"accept\":\"application/json\", \"Authorization\":\"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5\"}" ,status.INFO)

        obj.request.headers={"content-type":"application/json","accept":"application/json", "Authorization":"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5"}

        return obj

    def before_methodAPI(self,obj):

        obj.pg.addRow("Modifying Request api","Modified Request api while in Before Method<br><b>Request api: </b> https://apis-beta.gemecosystem.com/company" ,status.INFO)

        obj.request.api="https://apis-beta.gemecosystem.com/company"

        obj.pg.addRow("Modifying Request Method","Modified Request Method while in a Before Method<br><b>Request METHOD: </b>GET",status.INFO)

        obj.request.method="GET"

        return obj

    def before_apiMethodBodyHeaders(self,obj):

        if obj.legacy_req is not None and obj.legacy_req.api !='':

            obj.pg.addRow("Modifying Legacy Request api","Modified Legacy Request api while in Before Method<br><b>Legacy Request api: </b> https://gorest.co.in/public/v2/users" ,status.INFO)

            obj.legacy_req.api="https://gorest.co.in/public/v2/users"

            obj.pg.addRow("Modifying Legacy Request Method","Modified Legacy Request Method while in a Before Method<br><b>Legacy Request METHOD: </b>POST",status.INFO)

            obj.legacy_req.method="POST"

            email=random.random()

            obj.pg.addRow("Modifying Legacy Request Body","Modified Legacy Body while in Before Method<br><b>Legacy Request Body: </b> {\"name\": \" JOhn\",\"email\": f\"JOhn{email}@gmail.biz\",\"gender\": \"male\",\"status\": \"inactive\"}",status.INFO)

            obj.legacy_req.body={        

                    "name": " JOhn",

                    "email": f"JOhn{email}@gmail.biz",

                    "gender": "male",

                    "status": "inactive"

                }

            obj.pg.addRow("Modifying Legacy Request Headers","Modified Legacy Request Headers while in Before Method<br><b>Legacy Request Headers: </b>{\"content-type\":\"application/json\",\"accept\":\"application/json\", \"Authorization\":\"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5\"}" ,status.INFO)

            obj.legacy_req.headers={"content-type":"application/json","accept":"application/json", "Authorization":"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5"}

        else:

            obj.pg.addRow("Modifying Request api","Modified Request api while in Before Method<br><b>Request api: </b> https://gorest.co.in/public/v2/users" ,status.INFO)

            obj.request.api="https://gorest.co.in/public/v2/users"

            obj.pg.addRow("Modifying Request Method","Modified Request Method while in a Before Method<br><b>Request METHOD: </b>POST",status.INFO)

            obj.request.method="POST"

            obj.pg.addRow("Modifying Request Body","Modified Body while in Before Method<br><b>Request Body: </b> {\"name\": \" JOhn\",\"email\": f\"JOhn{email}@gmail.biz\",\"gender\": \"male\",\"status\": \"inactive\"}",status.INFO)

            obj.request.body={        

                    "name": " JOhn",

                    "email": f"JOhn{random.random()}@gmail.biz",

                    "gender": "male",

                    "status": "inactive"

                }

            obj.pg.addRow("Modifying Request Headers","Modified Request Headers while in Before Method<br><b>Request Headers: </b>{\"content-type\":\"application/json\",\"accept\":\"application/json\", \"Authorization\":\"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5\"}" ,status.INFO)

            obj.request.headers={"content-type":"application/json","accept":"application/json", "Authorization":"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5"}

        return obj

