class before:
    def before_(self, obj):
        obj.request.api="https://restcountries.com/v3.1/lang/german"
        obj.request.method="GET"
        return obj