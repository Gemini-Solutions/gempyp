from datetime import datetime
# from requests_ntlm import HttpNtlmAuth
import requests.auth
import logging
import traceback
import requests
import json
from getpass import getuser


class API:
    def __init__(self):
        pass

    def execute(self, request):
        EncryptKey = "Y4irRsiBmyGMBie5gAZ8va3IOHVOYZFxC5L1-jNydZk="
        result = Response()
        if not request.file:
            header_dict = {key.upper(): value.upper() for key, value in request.headers.items()}
            if "CONTENT-TYPE" not in header_dict.keys() or header_dict.get("CONTENT-TYPE", "") == "APPLICATION/JSON":
                try:
                    if not isinstance(request.body, str):
                        request.body = json.dumps(request.body)
                except Exception as e:
                    print("JSON object can not be serialized")
                    print(str(e))
            # write code for authentication 
            #if request.aythType.upper() == "KERBEROS":
            #   auth = HHTPKerberosAuth(request.authMethod, delegate=False)

            # else:
                # decrypt password

            #    password = self.decrypt(request.credentials.get("password", ""), EncryptKey)
            #    auth = HttpNtlmAuth(request.credentials.get("username", " "), password)
            try:
                start_time = end_time = datetime.now()
                obj = Response()
                if (
                    request.api == ""
                    or request.method == ""
                    or request.api is None
                    or request.method is None
                ):
                    raise Exception("Api and method are can not be empty or NULL")
                elif str.upper(request.method) == "POST":
                    start_time = datetime.now()
                    resp = requests.post(
                        request.api,
                        headers=request.headers,
                        files=request.file,
                        data=request.body,
                        verify=request.SSLVerify,
                        timeout=request.timeout // 1000
                    )
                    end_time = datetime.now()
                elif str.upper(request.method) == "GET":
                    start_time = datetime.now()
                    resp = requests.get(
                        request.api,
                        headers=request.headers,
                        files=request.file,
                        verify=request.SSLVerify,
                        timeout = request.timeout // 1000,
                    )
                    end_time = datetime.now()
                elif str.upper(request.method) == "PUT":
                    start_time = datetime.now()
                    resp = requests.put(
                        request.api,
                        headers=request.headers,
                        files=request.file,
                        data=request.body,
                        verify=request.SSLVerify,
                        timeout=request.timeout // 1000
                    )
                    end_time = datetime.now()
                elif str.upper(request.method) == "PATCH":
                    start_time = datetime.now()
                    resp = requests.patch(
                        request.api,
                        headers=request.headers,
                        files=request.file,
                        data=request.body,
                        verify=request.SSLVerify,
                        timeout=request.timeout // 1000
                    )
                    end_time = datetime.now()
                elif str.upper(request.method) == "DELETE":
                    start_time = datetime.now()
                    resp = requests.delete(
                        request.api,
                        headers=request.headers,
                        files=request.file,
                        data=request.body,
                        verify=request.SSLVerify,
                        timeout=request.timeout // 1000
                    )
                    end_time = datetime.now()
                else:
                    raise Exception("invalid method")

                obj.status_code = resp.status_code
                obj.response_body = resp.text
                obj.response_headers = resp.headers
                obj.response_time = resp.elapsed.total_seconds()

                if obj.response_time == 0:
                    elapsed_time = end_time - start_time
                    obj.response_time = elapsed_time.total_seconds()
                logging.info(f"URL: {request.api}")
                logging.info(f"Time elapsed: {obj.response_time} secs")

                result = obj
            except Exception as e:
                print(traceback.format_exc())
                print(str(e))
                result = obj
            
            # add retries if required
            return result
        
        pass


    def decrypt(self, encrypted_Password, key=None):
        # decrypt the password based on the key if no key is provided default key will be used
        result = None
        try:
            if not key:
                user = getuser()
                key= self.get_key(user)
                result = self.decrypt_(encrypted_Password, key)
        except Exception as e:
            print("Error: " + str(e))
        return result

    def decrypt_(self):
        pass

    def get_key(self):
        pass


class Request:
    def __init__(self):
        self.api = ""
        self.method = "method"
        self.headers = {}
        self.body = {}
        self.file = ""
        self.SSLVerify = False
        self.timeout = 30000


class Response:
    def __init__(self, body="", code=200, response_time=0, headers={}):
        self.response_body = body
        self.status_code = code
        self.response_time = response_time
        self.response_headers = headers
