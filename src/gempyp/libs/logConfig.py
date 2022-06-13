from fileinput import filename
from stat import filemode
import sys, os
from tkinter import W
import coloredlogs, logging

class LoggingConfig:
    def __init__(self, file_name='tmp.log') -> None:
        # logging.basicConfig(filename=file_name,
        #             format='%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s',
        #             datefmt='%H:%M:%S',
        #             filemode='w',
        #             level=logging.INFO)
        self.mylogs = logging.getLogger()
        fieldstyle = {'asctime': {'color': 'green'},
                    'levelname': {'bold': True, 'color': 'white'},
                    'filename':{'color':'cyan'},
                    'funcName':{'color':'blue'}}
                                        
        levelstyles = {'critical': {'bold': True, 'color': 'red'},
                    'debug': {'color': 'green'}, 
                    'error': {'color': 'red'}, 
                    'info': {'color':'white'},
                    'warning': {'color': 'yellow'}}

        coloredlogs.install(level=logging.INFO,
                            logger=self.mylogs,
                            fmt='%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s',
                            datefmt='%H:%M:%S',
                            field_styles=fieldstyle,
                            level_styles=levelstyles)
        file = logging.FileHandler(filename=file_name, mode='w')
        fileformat = logging.Formatter('%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s',
        datefmt='%d-%m-%Y, %H:%M:%S')
        file.setFormatter(fileformat)
        self.mylogs.addHandler(file)

def my_custom_logger(logger_name, level=logging.INFO):
    """
    Method to return a custom logger with the given name and level
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    format_string = '%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s'
    log_format = logging.Formatter(format_string, datefmt='%d-%m-%Y, %H:%M:%S')
    # Creating and adding the console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    # Creating and adding the file handler
    file_handler = logging.FileHandler(logger_name, mode='w')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    return logger
        
