from pygem.pi_rest.rest_obj import REST_Obj


class before:
    def before_(self, obj):
        print("---------------------------------inside before method--------------------------------------")
        print("PROJECT", obj.project)
        obj.project = "ABC"
        return obj


if __name__ == "__main__":
    obj = before().before_(REST_Obj(project="SOME_PROJECT"))