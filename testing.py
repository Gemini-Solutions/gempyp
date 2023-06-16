import requests

def send_form_data(url, files,headers,form_data=None):
    response = requests.post(url, data=form_data, files=files,headers=headers,verify=True)
    return response

# Example usage:
url = 'https://devapi.geminisolutions.com/atsJobSvc/job'
files = [
    ('jdFile', open('C:\\Users\\Tanya.Agarwal\\Downloads\\ScribbleCheatSheet.txt', 'rb'))
]
form_data={'job': {'dcName': 'DC-ANDROID', 'ecName': 'EC-JAVA', 'jobProfile': 'Demo Created', 'hireType': 'Replacement', 'jobStatus': 1, 'minExp': 7, 'maxExp': 50, 'priority': 'L', 'clientName': 'PIMCO', 'primarySkills': 'Java', 'reqQuantity': 7, 'internalHiringAllowed': True, 'jobFulfilmentDate': '2023-04-27', 'fileName': 'JD_DevOps engg_pdf', 'documentHash': '0675BD28BBCA8F621784D7F43DD1789A', 'contentType': 'application/pdf', 'content': '', 'isActive': True, 'country': 'Antarctica', 'hiringOwner': 'Tripta Sahni', 'isBillable': True, 'orderId': 0, 'jobId': 3366}}
headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJhcGk6Ly80ZjY4NWQ3Ni1lMjQzLTRmZjUtOTM2OC03MDQ4Mzc3ZDc3MDkiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9iOTgwNmM3ZC05MjgwLTRlNDQtYWZlYS02ZGMwZmY0OTVjMmYvIiwiaWF0IjoxNjg2ODk5NDcxLCJuYmYiOjE2ODY4OTk0NzEsImV4cCI6MTY4NjkwMzM3MSwiYWlvIjoiRTJaZ1lKaDQzYnZBME01a3ZZV2ZWY0hjZCt2MkF3QT0iLCJhcHBpZCI6IjRmNjg1ZDc2LWUyNDMtNGZmNS05MzY4LTcwNDgzNzdkNzcwOSIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2I5ODA2YzdkLTkyODAtNGU0NC1hZmVhLTZkYzBmZjQ5NWMyZi8iLCJvaWQiOiI1ZjUyYzExMC1mODg0LTRhNjctYjhiMi00YzBiNTZjNmYwNmYiLCJyaCI6IjAuQVhFQWZXeUF1WUNTUkU2djZtM0FfMGxjTDNaZGFFOUQ0dlZQazJod1NEZDlkd21IQUFBLiIsInN1YiI6IjVmNTJjMTEwLWY4ODQtNGE2Ny1iOGIyLTRjMGI1NmM2ZjA2ZiIsInRpZCI6ImI5ODA2YzdkLTkyODAtNGU0NC1hZmVhLTZkYzBmZjQ5NWMyZiIsInV0aSI6IkhxdHg4ZVl3amstNUlYQTE1N2N5QUEiLCJ2ZXIiOiIxLjAifQ.NkJ2xfq-labPB_l8C-0yLYDFaOnLCeGzx9jKgjczfwDuHlyYOK2zOELulMiLLlhGW7na5RR0pF5ItEWWLE1IGVtnkqgxjumo_AxhnCpSGkX5_9oVZJWXW9ZNI-nTxvTrweK6m9u5GctjkGe67zUHyGYwFWZJbsjxXrwHvCIqWjw2benGIZnchvCPwu1vj0owhr3VQGYhQORIDpyKCCuSf3fO-JsjzlH80AdZ9tSqr39JkONRu_-1UZvLLauNZ1oQvWwPk_4EsMLe7WOvWJjGewySp8mQGXd22vNgOd2iPRN1ugjwLlQonX0sr08pcu86AtckxdgwZXiZrVuuHtKVXg', 'X-REMOTE-USER-EMAIL': 'saru.goyal@geminisolutions.com'}
response = send_form_data(url, files,headers)
print(response.status_code)
print(response.text)
print(response.request.headers)
 # Assuming the response is in JSON format
