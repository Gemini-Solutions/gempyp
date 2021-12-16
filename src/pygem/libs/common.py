import json
from datetime import datetime
import traceback
from pygem.config import DefaultSettings


def read_json(file_path):
    try:
        #print(file_path)
        with open(file_path) as fobj:
            res = json.load(fobj)
    except Exception:
        res = None
    return res

def findDuration(start_time: datetime, end_time: datetime):
    # finds the duration in the form HH MM SS

    duration = end_time - start_time
    seconds = duration.total_seconds()
    mins = seconds/60
    seconds = seconds%60

    if mins > 0:
        return f"{mins} mins and {seconds} seconds"
    return f"{seconds} seconds"


def errorHandler(logger, Error, msg = "some Error Occured"):
    
    logger.error(msg)
    logger.error(f"Error: {Error}")

    if DefaultSettings.DEBUG:
        logger.error(f"TraceBack: {traceback.format_exc()}")













