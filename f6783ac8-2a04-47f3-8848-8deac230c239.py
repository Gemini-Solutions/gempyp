from gempyp.libs.enums.status import status

class beforeAfter:

    def before_method(self,obj):

        obj.pg.addRow("Modifying Request Method","Modified Request Method while in a Before Method<br><b>Request METHOD: </b>GET",status.INFO)

        obj.request.method="GET"


        return obj