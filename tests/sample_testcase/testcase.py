from gempyp.pyprest import apiCommon as api

def before(self, obj):
        obj.request=api.Request()
        obj.request.api="https://gorest.co.in/public/v2/users"
        obj.request.method="POST"
        obj.request.body="{\"name\": \" JOhn\",\"email\": \"JOhn@gmail.biz\",\"gender\": \"male\",\"status\": \"inactive\"}"
        obj.request.headers={"content-type":"application/json","accept":"application/json", "$[#auth]":"Bearer 7cf300a3954980370df0803705cb1fb157b4dea84eecf0f2d206f41d48c4a8b5"}
        return obj


        