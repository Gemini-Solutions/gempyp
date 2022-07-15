
from gempyp.engine.simpleTestcase import AbstractSimpleTestcase
from gempyp.pyprest.restObj import RestObj
from gempyp.pyprest import apiCommon as api


class fetchBody(AbstractSimpleTestcase):
    obj=RestObj()
    def body(self,obj):
        print(obj.variables)
        return obj


        