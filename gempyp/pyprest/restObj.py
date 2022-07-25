class RestObj:
    def __init__(self, **kwargs):
        if "pg" in kwargs:
            self.pg = kwargs['pg']
        if "project" in kwargs:
            self.project = kwargs["project"]
        if "request" in kwargs:
            self.request = kwargs["request"]
        if "response" in kwargs:
            self.response = kwargs["response"]
        if "tcname" in kwargs:
            self.tcname = kwargs["tcname"]
        if "variables" in kwargs:
            self.variables = kwargs["variables"]
        if "legacy_res" in kwargs:
            self.legacy_res = kwargs["legacy_res"]
        if "legacy_req" in kwargs:
            self.legacy_req = kwargs["legacy_req"]
        if "request_file" in kwargs:
            self.request_file = kwargs["request_file"]
        if "env" in kwargs:
            self.env = kwargs["env"]

    @property
    def returnObj():
        return RestObj()
