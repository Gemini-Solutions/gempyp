from abc import ABC, abstractmethod


class baseConfig(ABC):

    def __init__(self, *args, **kwargs):
        self.parser(*args, **kwargs)
        isValid = self.isValid()
        if not isValid:
            raise Exception  # change this to your custom exception
        
    

    @abstractmethod
    def parser(self, *args, **kwargs):
        pass


    def isValid(self):
        pass


        

