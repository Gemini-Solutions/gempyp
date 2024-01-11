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
import os


class Api:
    def __init__(self):
        pass

    def execute(self, request):
        encrypt_key = "Y4irRsiBmyGMBie5gAZ8va3IOHVOYZFxC5L1-jNydZk="
        result = Response()
        # if not request.file:
        header_dict = {key.upper(): value.upper() for key, value in request.headers.items()}
        if header_dict.get("CONTENT-TYPE", "") == "APPLICATION/JSON":
                try:
                    if not isinstance(request.body, str):
                        request.body = json.dumps(request.body)
                except Exception as e:
                    logging.info("JSON object can not be serialized")
                    logging.info(str(e))
        else:
                try:
                    newFile=[]
                    newBody={}
                    for key,value in request.body.items():
                        newFileTuple=tuple()
                        if(isinstance(value,str) and os.path.isfile(value)):
                            name = value.split('/')[-1]
                            newFileTuple+=(key,(name,open(value,'rb')))
                            newFile.append(newFileTuple)
                        else:
                            if(isinstance(value,dict)):
                                newBody[key]=str(json.dumps(value))
                            else:
                                newBody[key]=value
                    request.file=newFile
                    request.body=newBody
                    # request.body = self.convert_quotes_boolean(request.body)
                    pass
                except Exception as e:
                    traceback.print_exc()
                    logging.info("JSON object can not be serialized")
                    logging.info(str(e))
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
                resp, start_time, end_time = self.make_request(request)

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
                traceback.print_exc()
                logging.info(str(e))
                result = obj
            
            # add retries if required
        if request.retries > 0:
                if result.status_code not in request.expected_code_list:
                    request.retries -= 1
                    logging.info("retrying...........")
                    time.sleep(1)
                    return self.execute_api(request)
        
        return result

    def make_request(self,request):
        METHODS = {
            "POST": requests.post,
            "GET": requests.get,
            "PUT": requests.put,
            "PATCH": requests.patch,
            "DELETE": requests.delete,
        }
        if not request.api or not request.method:
            raise Exception("Api and method cannot be empty or NULL")

        # Convert method to uppercase for consistency
        method = request.method.upper()

        if method not in METHODS:
            raise Exception("Invalid method")

        # Define headers, files, data, and authentication based on the request
        auth = None
        if request.auth and request.auth.upper() == "PASSWORD":
            auth = (request.username, request.password)

        headers = request.headers
        files = request.file
        data = request.body
        verify = request.SSLVerify
        timeout = request.timeout

        # Make the request and calculate the time taken
        start_time = datetime.now()
        try:
            resp = METHODS[method](
            request.api,
            headers=headers,
            files=files,
            data=data,
            verify=verify,
            auth=auth,
            timeout=timeout
        )
            end_time = datetime.now()
            return resp, start_time, end_time   
        except Exception as e:
            end_time = datetime.now()
            logging.info("Error while making {http_method} to the {api}".format(http_method=method, api=request.api))
            traceback.format_exception_only()
            return resp, start_time, end_time   
                  



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
            logging.info(e)
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
            logging.info(e)
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
        self.timeout = 330000
        self.auth = ""
        self.expected_code_list = []
        self.retries = 0


class Response:
    def __init__(self, body="", code=504, response_time=0, headers={}):
        self.response_body = body
        self.status_code = code
        self.response_time = response_time
        self.response_headers = headers
