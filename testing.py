import requests
url = "https://v3.1/lang/germans"



resp = requests.get(url, headers={"Content-Type": "application/json"})
print(resp.status_code)