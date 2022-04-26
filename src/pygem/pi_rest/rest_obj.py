class REST_Obj:
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
        if "suite_variables" in kwargs:
            self.suite_variables = kwargs["suite_variables"]
        if "legacy_res" in kwargs:
            self.legacy_res = kwargs["legacy_res"]
        if "request_filet" in kwargs:
            self.request_file = kwargs["request_file"]
        if "env" in kwargs:
            self.env = kwargs["env"]

    @property
    def return_obj():
        return REST_Obj()
