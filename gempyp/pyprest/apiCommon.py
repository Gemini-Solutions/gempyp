import json
import logging
from time import time
import traceback
from datetime import datetime
from getpass import getuser
import warnings
from cryptography.fernet import Fernet
import requests
import requests.auth
from requests_ntlm import HttpNtlmAuth


class Api:
    def __init__(self):
        pass

    def execute(self, request):
        encrypt_key = "Y4irRsiBmyGMBie5gAZ8va3IOHVOYZFxC5L1-jNydZk="
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
            # decrypt password
            auth = None
            try:
                if request.auth.upper() == "PASSWORD":
                    password = self.decrypt_(request.credentials.get("password", ""), encrypt_key)
                    auth = HttpNtlmAuth(request.credentials.get("username", " "), password)
            except Exception as e:
                logging.info("Error occured while creating the auth object- " + str(e))
                auth = None
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
                    if request.auth.upper() == "PASSWORD":
                        resp = requests.post(
                            request.api,
                            headers=request.headers,
                            files=request.file,
                            data=request.body,
                            verify=request.SSLVerify,
                            auth=auth,
                            timeout=request.timeout // 1000
                        )
                    else:
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
                    if request.auth.upper() == "PASSWORD": 
                        resp = requests.get(
                            request.api,
                            headers=request.headers,
                            files=request.file,
                            verify=request.SSLVerify,
                            auth=auth,
                            timeout=request.timeout // 1000,
                        )
                    else:
                        resp = requests.get(
                            request.api,
                            headers=request.headers,
                            files=request.file,
                            verify=request.SSLVerify,
                            timeout=request.timeout // 1000,
                        )
                    end_time = datetime.now()
                elif str.upper(request.method) == "PUT":
                    start_time = datetime.now()
                    if request.auth.upper() == "PASSWORD": 
                        resp = requests.put(
                            request.api,
                            headers=request.headers,
                            files=request.file,
                            data=request.body,
                            auth=auth,
                            verify=request.SSLVerify,
                            timeout=request.timeout // 1000
                        )
                    else:
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
                    if request.auth.upper() == "PASSWORD": 
                        resp = requests.patch(
                            request.api,
                            headers=request.headers,
                            files=request.file,
                            data=request.body,
                            verify=request.SSLVerify,
                            auth=auth,
                            timeout=request.timeout // 1000
                        )
                    else:
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
                    if request.auth.upper() == "PASSWORD":
                        resp = requests.delete(
                            request.api,
                            headers=request.headers,
                            files=request.file,
                            data=request.body,
                            verify=request.SSLVerify,
                            auth=auth,
                            timeout=request.timeout // 1000
                        )
                    else:
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
            if request.retries > 0:
                if result.status_code not in request.expected_code_list:
                    request.retries -= 1
                    logging.info("retrying...........")
                    time.sleep(1)
                    return self.execute_api(request)
            return result

    def encrypt_(self, password, key):
        try:
            fernet_ = Fernet(key)
            # supress user warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                enc_pass = fernet_.encrypt(password)
        except Exception as e:
            enc_pass = None
            traceback.print_exc()
            print(e)
        return enc_pass

    def decrypt_(self, enc_pass, key):
        try:
            fernet_ = Fernet(key)
            # supress user warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                enc_pass = enc_pass.encode('utf-8')
                dec_pass = fernet_.decrypt(enc_pass)
                dec_pass = dec_pass.decode('utf-8')
        except Exception as e:
            dec_pass = None
            traceback.print_exc()
            print(e)
        return dec_pass


class Request:
    def __init__(self):
        self.api = ""
        self.method = "method"
        self.headers = {}
        self.body = {}
        self.file = ""
        self.SSLVerify = False
        self.credentials = {}
        self.timeout = 30000
        self.auth = ""
        self.expected_code_list = []
        self.retries = 0


class Response:
    def __init__(self, body="", code=200, response_time=0, headers={}):
        self.response_body = body
        self.status_code = code
        self.response_time = response_time
        self.response_headers = headers
