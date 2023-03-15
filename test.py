import requests
if __name__ == "__main__":
    headers={"bridgeToken":"d8f96e13-0f0a-422e-8d4e-6094263f95031676026857646", "username":"geco-tanya"}
    api="https://apis-beta.gemecosystem.com/v1/upload/file"
    data=[
  ('file',('GEMPYPFAQ.xml',open('C://Users//Tanya.Agarwal//GEMPYPFAQ.xml','rb'),'text/xml'))
]
    r = requests.post(api, files=data,headers=headers)
    print(data)
    print(r.text)
    print(r.status_code)

