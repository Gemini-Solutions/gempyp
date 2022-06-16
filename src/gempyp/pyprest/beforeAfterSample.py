from gempyp.pyprest.restObj import RestObj


# create an object of PYPREST helper and take that object in your before and after methods,then return it.

class before:
    def before_(self, obj):
        print("---------------------------------inside before method--------------------------------------")
        print("PROJECT", obj.project)
        obj.project = "ABC"
        return obj


if __name__ == "__main__":
    obj = before().before_(RestObj(project="SOME_PROJECT"))