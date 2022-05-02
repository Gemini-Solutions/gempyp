import os
import json
import logging as log
from datetime import datetime
import traceback
from typing import List, Union
import typing
from gempyp.config import DefaultSettings


def read_json(file_path):
    try:
        # print(file_path)
        with open(file_path) as fobj:
            res = json.load(fobj)
    except Exception:
        res = None
    return res


def findDuration(start_time: datetime, end_time: datetime):
    # finds the duration in the form HH MM SS

    duration = end_time - start_time
    seconds = duration.total_seconds()
    mins = seconds // 60
    seconds = seconds % 60

    if mins > 0:
        return f"{mins} mins and {round(seconds, 3)} seconds"
    return f"{round(seconds, 3)} seconds"


def errorHandler(logger, Error, msg="some Error Occured"):

    logger.error(msg)
    logger.error(f"Error: {Error}")

    if DefaultSettings.DEBUG:
        logger.error(f"TraceBack: {traceback.format_exc()}")


def parseMails(mail: Union[str, typing.TextIO]) -> List:
    try:

        if hasattr(mail, "read"):
            mails = mail.read()

        elif os.path.isfile(mail):
            file = open(mail, "r")
            mails = file.read()
            file.close()

        mails = mail.strip()
        mails = mails.split(",")
        return mails
    except Exception as e:
        log.error("Error while parsing the mails")
        log.error(f"Error : {e}")
        log.error(f"traceback: {traceback.format_exc()}")
        return []


# custom encoder to encode date to epoch
class dateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()*1000

        return json.JSONEncoder.default(self, o)
