from gempyp.libs.enums.status import status
class beforeAfter:
    def after_(self,obj):
        if(obj.response.status_code==200):
            obj.pg.addRow("Respone code validation","Details inserted successfully",status.PASS)
        if(obj.response.status_code==400):
            obj.pg.addRow("Respone code validation","Invalid employee id. Data not inserted",status.PASS)
        return obj
    def before_(self,obj):
        obj.request.body={'experience': '5'}
        return obj