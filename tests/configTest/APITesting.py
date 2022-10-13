import os
import requests
def file_upload(json_form_data): 
        files_data=[]
        json_form_data_1={}  
        for key,value in json_form_data.items():
            files_data_tuple=tuple()
            if(os.path.exists(json_form_data[key])):
                files_data_tuple+=(key,json_form_data[key])
            files_data.append(files_data_tuple)
        json_form_data_1["files"]=files_data
        return json_form_data_1


url="https://apis-beta.gemecosystem.com/v1/upload/file?tag=PUBLIC&amp;folder=x/y"
files_1=file_upload({"file":"C:\\Users\\ta.agarwal\\Desktop\\automation.txt"})
r = requests.post(url, files=files_1["files"],headers={"username":"tanya.agarwal","bridgetoken":"374efe42-323e-4445-b89b-1ff750f000c61664541163883"})
print(r.text)