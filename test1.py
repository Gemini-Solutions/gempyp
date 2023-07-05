import traceback

from gempyp.sdk.executor import Executor

from gempyp.libs.enums.status import status





def new_meth():

    obj = Executor()

    obj.reporter.addRow("test", "test", status.PASS)




if __name__ == "__main__":

    try:

        new_meth()

    except Exception as e:

        traceback.print_exc()