class DvObj:
    def __init__(self, **kwargs):
        """
        source_df and target_df will contains the source and target dataframe
        source_columns and target_columns will contain columns name 
        if we do any change in df columns in before method than we need to do it in source_columns too

        self.keys will always be given in list

        value_df will contain mismatch for values and keys_df will contain the mismatch for keys 
        """
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
