import requests

import json

import urllib3




body = {'applicantData': '{"firstName":"gauri","lastName":"shankar","currentLocation":"Kolkata","totalYearOfExperience":"4","relevantExperience":"3","source":"Campus","primarySkill":"tret","skillCategory":".Net","webLink":"htttp://cwecew.com","gender":"Male","additionalRemarks":"fdv df ","referredBy":"Aashish Khiste","experiences":[{"jobTitle":"java developer","employmentType":"full time","companyName":"zadax informatics","location":"pune","fromDate":"","toDate":"","description":"","currentlyWorking":"true"}],"qualifications":[{"instituteName":"sdvsd","city":"ciriie","qualification":"efse","stream":"fdvsvsdvsd","percentage":"98","fromDate":"2023-02-10 00:00:00","toDate":"2023-02-20 00:00:00","currentlyAttending":""}],"currentStageId":1,"email":"ddhjdg109jfh@gmail.com","contactNumber":687491061008}'}
headers = {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJhcGk6Ly80ZjY4NWQ3Ni1lMjQzLTRmZjUtOTM2OC03MDQ4Mzc3ZDc3MDkiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9iOTgwNmM3ZC05MjgwLTRlNDQtYWZlYS02ZGMwZmY0OTVjMmYvIiwiaWF0IjoxNjg3NzY5MDk0LCJuYmYiOjE2ODc3NjkwOTQsImV4cCI6MTY4Nzc3Mjk5NCwiYWlvIjoiRTJaZ1lIZ3RwZVB6elVmVStJSG5qQmJ4aStmUEFnQT0iLCJhcHBpZCI6IjRmNjg1ZDc2LWUyNDMtNGZmNS05MzY4LTcwNDgzNzdkNzcwOSIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2I5ODA2YzdkLTkyODAtNGU0NC1hZmVhLTZkYzBmZjQ5NWMyZi8iLCJvaWQiOiI1ZjUyYzExMC1mODg0LTRhNjctYjhiMi00YzBiNTZjNmYwNmYiLCJyaCI6IjAuQVhFQWZXeUF1WUNTUkU2djZtM0FfMGxjTDNaZGFFOUQ0dlZQazJod1NEZDlkd21IQUFBLiIsInN1YiI6IjVmNTJjMTEwLWY4ODQtNGE2Ny1iOGIyLTRjMGI1NmM2ZjA2ZiIsInRpZCI6ImI5ODA2YzdkLTkyODAtNGU0NC1hZmVhLTZkYzBmZjQ5NWMyZiIsInV0aSI6IlhMRnU1eGh5MGtTUGwtYXJLbXNqQUEiLCJ2ZXIiOiIxLjAifQ.pP0SERgGVp6sh0j5XgFovtl-9Z-WsvLSEOoDJhiEaVvlSzvkUEVmnoCBCQXjgSJ2E3Z72iIIWHRBlVF7kQv4kr3josTSP0HsTWbrmi-GqqLs_LTPu9lom1smbmqPA0xEBPEjPXhzyJSd47uihETw_W8L_jeOAq6fCxfv8g068p1Aq33AiKX-nxSHlI62uJcZDC7XOH76ThM6jLM7G0WBZfkBh3VDQe62FcdPXrgCG7topx26gEyah5iIL8RkDnVLX-Tm79tPJ7MoP_dYbHw686LwJRz6qeZuJpDZX97PFk7jRjkY5sGOAp3TCly3JRV_ox40VRrxIO9v3CK98mXv2Q","X-REMOTE-USER-EMAIL":"saru.goyal@geminisolutions.com"}

files=[
    ("image", open("C:\\Users\\Tanya.Agarwal\\Downloads\\Linkdln_XYZ(5-6).pdf", 'rb')), 
    ("resume", open("C:\\Users\\Tanya.Agarwal\\Downloads\\Linkdln_XYZ(5-6).pdf", 'rb'))
]
# eader = urllib3.encode_multipart_formdata(body)

url = "https://devapi.geminisolutions.com/atsApplicantSvc/applicant"
response=requests.request("POST", url, headers=headers, data=body, files=files)
print(response.status_code)
print(response.text)