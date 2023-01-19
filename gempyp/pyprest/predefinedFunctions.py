from datetime import datetime, date, timedelta
from sqlite3 import TimeFromTicks
import time
import traceback
import pytz
import random
import uuid


#TODO: functions we can add in the predefined functions 
"""
getDate according to time zone.
getTime according to time zone.
getUniqueNo in the given range
randomNo number
random out of a list
generate list of values(start value, end val, iterator val)
getdatetime(format, offset, timezone)
transform_date(date,offset,timezone)

"""



class PredefinedFunctions:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        # logger.info("________________________________ Inside Predefined Functions _________________________________________")
        self.date_formats = {
            'ddmmyyyy': '%d/%m/%Y',
            'ddmonyyyy': "%d %b, %Y",
            'monddyyyy': '%b %d, %Y',
            'ddmmyy': '%d%m%y',
        }  # add mode datetime formats


    def parseParams(self, param_str):
        """parsing string parameters ( all the params are strings )"""
        if '[' in param_str:
            br_start = param_str.find('[')
            br_end = param_str.find(']')
            list_ = param_str[br_start + 1:br_end].split(",")
            params_list = param_str[:br_start].split(",") + [list_] + param_str[br_end + 1:].split(",")
            params_list = [i for i in params_list if i != '' and i != " "]

        else:
            params_list = param_str.split(",")
        if len(params_list) > 0:
            params_list = [each.strip(" ") if isinstance(each, str) else each for each in params_list]
        return params_list

    def rand(self, start, end):
        """get random number out of a given range"""
        try:
            if int(start) < int(end):
                self.rand_number = random.randint(int(start), int(end))
                return self.rand_number
            else:
                self.pyprest_obj.logger.info("Start and end values are not defined properly")
        except Exception as e:
            self.pyprest_obj.logger.error(str(e)) 

    # return uuid
    def uuid(self, *kwargs):
        return str(uuid.uuid4())    

    def epoch(self, str):
        """
        Return epoch time in seconds
        if "milli" is passed as a parameter then returns time in epoch milli"""
        millis = False
        type = self.parseParams(str)
        if len(type) > 0:
            if "mil" in type[0].lower():
                millis = True
        try:
            if millis == True:
                return round(time.time()*1000, 0)
            else:
                return round(time.time(), 0)
        except Exception as e:
            self.pyprest_obj.logger.info(str(e))

    def unique(self, len_):
        """
        Return unique number of the length given"""
        len_ = int(len_.strip('"').strip("'"))
        number_ = str(str(time.time()*1000).split('.')[0])
        number_ = self.numberGenerator(number_, len_)
        start = len(str(number_)) - len_
        number_ = int(number_[start:])
        return number_

    def numberGenerator(self, num, len_):
        """generate a number greater than the length given"""
        if len_ > len(num):
            num = num + num
            if len_ > len(num):
                return self.numberGenerator(num, len_)
            else:
                return num
        else:
            return num


    #get random element from a list
    def getRandomFromAlist(self, listName):
        """
        acceps a list of elements.
        Returns a random element from the lists
        """
        try:
            startIdxList = 0 
            endIdxList = len(listName)-1
            randIndex = random.randint(startIdxList, endIdxList)
            return listName[randIndex]
        except Exception as e:
            self.pyprest_obj.logger.info(str(e))   


    #get date from now function it will add a value which is provided as a parameter to the current date and will return it to the use.
    def getDateFromNow(self, *args):
        """
        get date from now function it will add a value which 
        is provided as a parameter to the current date and will return it to the use.

        params_str should contain comma separated values-
        days,
        date format """
        n_value = int(args[0].strip('"').strip("'"))
        try:
            date_format = args[1].strip('"').strip("'")
        except Exception as e:
            self.pyprest_obj.logger.info(traceback.format_exc())
            date_format = 'ddmmyyyy'
        try:
            self.data_N_days_after = date.today() + timedelta(days = int(n_value))
            self.value = self.data_N_days_after.strftime(str(self.date_formats[date_format]))
            return self.value
        except Exception as e:
            self.pyprest_obj.logger.info(traceback.format_exc())
            self.pyprest_obj.logger.info("Error occured while excuting getDateFromNow() function")

    # getDate function with format
    def curr_timestamp(self, dateformat="", tz="UTC"):
        """
        return current datetime in required format
        if user gives a timezone, he/she will get time in that timezone
        
        currently supported date formats are-
        ddmmyy
        ddmonyyyy
        ddmmyyyy
        monddyyyy
        .
        """
        current_timestamp = datetime.now().strftime("%d%m%y")
        try: 
            self.pyprest_obj.logger.info("inside get date ")
            if not tz:
                date_time = datetime.now()
            else:
                date_time  = datetime.now(pytz.timezone(tz))
            try:
                current_timestamp = date_time.strftime(self.date_formats.get(dateformat.strip('"').strip("'").lower(), '%d%m%y'))
            except Exception as e:
                self.pyprest_obj.logger.info(str(e))
        except Exception as e:
            self.pyprest_obj.logger.info(str(e))
        return current_timestamp
        

    # TODO
    #get time function with timezone, time_format, twenty_four_hour_format
    def getTime(self,tz = "", time_format = "", twenty_four_hour_Format = True):
        try:
            self.pyprest_obj.logger.info("Execution of getTime")
            try:
                # print(tz)
                if not tz: 
                    date_time = datetime.datetime.now()  
                else:
                    try:
                        date_time = datetime.datetime.now(pytz.timezone(tz))
                    except Exception as e:
                         self.pyprest_obj.logger.info(str(e))
            except Exception as e:
                self.pyprest_obj.logger.info(str(e))
            if not time_format and  twenty_four_hour_Format is False  :
                self.current_time = date_time.strftime("%I:%M:%S")
            elif not time_format and twenty_four_hour_Format is True:
                self.current_time = current_time = date_time.strftime("%H:%M:%S")
            elif time_format == "hh:mm" and twenty_four_hour_Format is False :
                 self.current_time = date_time.strftime("%I:%M")
                 if int(date_time.strftime("%H"))>=12:
                    return self.current_time+" PM"
                 else:
                    return self.current_time+" AM"
            elif time_format == "hh:mm" and twenty_four_hour_Format is True :
                self.current_time = date_time.strftime("%H:%M")
            elif twenty_four_hour_Format is False:
                
                self.current_time = date_time.strftime("%I:%M:%S")
                if(int(date_time.strftime("%H"))>=12):
                    return self.current_time+" PM"
                else:
                    return self.current_time+" AM"
            else:
                self.current_time = date_time.strftime("%H:%M:%S")
            return self.current_time
        except Exception as e:
            self.pyprest_obj.logger.info(str(e))

    def generateListofValues(self, start_val, end_val, iter_val):
        pass

    def alpha(self, *args):
        pass
        