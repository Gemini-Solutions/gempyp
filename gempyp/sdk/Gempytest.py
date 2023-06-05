from gempyp.sdk.executor import Executor
from gempyp.libs.enums.status import status
import pytest

class gem_pytest(Executor):
    status = status
    gpytest = pytest

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    
        # try:
        #         pytest.main()
        # except AssertionError as e:
        #         logging.info("Assertion error"+ str(e))

    
    # def runner(self):
    #     if self.path is not None:
    #         try:
    #             pytest.main([self.path])
    #         except AssertionError as e:
    #             logging.info("Assertion error"+ str(e))
