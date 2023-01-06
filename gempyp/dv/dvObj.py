class DvObj:
    def __init__(self, **kwargs):
        if "pg" in kwargs:
            self.pg = kwargs['pg']
        if "project" in kwargs:
            self.project = kwargs["project"]
        if "source_df" in kwargs:
            self.source_df = kwargs["source_df"]
        if "target_df" in kwargs:
            self.target_df = kwargs["target_df"]
        if "source_columns" in kwargs:
            self.source_columns = kwargs["source_columns"]
        if "target_columns" in kwargs:
            self.target_columns = kwargs["target_columns"]
        if "keys" in kwargs:
            self.keys = kwargs["keys"]
        if "env" in kwargs:
            self.env = kwargs["env"]
        if "value_df" in kwargs:
            self.value_df = kwargs["value_df"]
        if "keys_df" in kwargs:
            self.keys_df = kwargs["keys_df"]

    @property
    def returnObj():
        return DvObj()
