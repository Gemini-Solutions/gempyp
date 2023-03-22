from traceback import print_exc, print_stack
import traceback
from gempyp.libs.enums.status import status
import logging


##   check if actual value is string or not

def compareTo(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """checks for equality of actual value and expected value. 
    OPERATOR -"to"
    """
    actual_value = key_val_dict.get(key, key)
    if isinstance(actual_value, (int, float)):
        actual_value = str(actual_value)
        exp_value = str(value.strip('"').strip("'"))
    else:
        actual_value = str(actual_value).lower()
        exp_value = value.strip('"').strip("'").lower()
        
    if actual_value == exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = To",status.PASS, CURRENT_API = "-",LEGACY_API = f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied" )
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = To",status.PASS, CURRENT_API=f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = To",status.FAIL, CURRENT_API="-",LEGACY_API = f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied" )
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = To",status.FAIL, CURRENT_API=f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied", status.FAIL)
        obj.addMisc("REASON OF FAILURE", "Mismatches found during Assertion")


    return obj


def compareToResp(obj,key,value, key_val_dict, key_val_dict_legacy, keyCheckResult, tolerance):
    try:
        actual_value = key_val_dict.get(key,key)
        required_value = key_val_dict_legacy[value]
        if keyCheckResult == "FOUND":
            if actual_value == required_value:
                if 'legacy' in key:
                    obj.addRow(f"Comparing  |  Respective values of {key} and {value}",f"Check if values are equal.",status.PASS, CURRENT_API=f"Value for {value} is {key_val_dict_legacy[value]}", LEGACY_API=f"Value for {key} is {key_val_dict[key]}")
                else:
                    obj.addRow(f"Comparing  |  Respective values of {key} and {value}",f"Check if values are equal",status.PASS, CURRENT_API=f"Value for {key} is {key_val_dict[key]}", LEGACY_API=f"Value for {value} is {key_val_dict_legacy[value]}")
            else:
                if 'legacy' in key:
                    obj.addRow(f"Comparing  |  Respective values of {key} and {value}",f"Check if values are equal",status.FAIL, CURRENT_API=f"Value for {value} is {key_val_dict_legacy[value]}", LEGACY_API=f"Value for {key} is {key_val_dict[key]}")
                else:
                    obj.addRow(f"Comparing  |  Respective values of {key} and {value}",f"Check if values are equal",status.FAIL, CURRENT_API=f"Value for {key} is {key_val_dict[key]}", LEGACY_API=f"Value for {value} is {key_val_dict_legacy[value]}")
    except:
        traceback.print_exc()

def compareNotToResp(obj,key,value, key_val_dict, key_val_dict_legacy, keyCheckResult, tolerance):
    try:
        actual_value = key_val_dict.get(key,key)
        required_value = key_val_dict_legacy[value]
        if keyCheckResult == 'FOUND':
            if actual_value != required_value:
                if 'legacy' in key:
                    obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"Check if values are not equal.",status.PASS, CURRENT_API=f"Value for {value} is {key_val_dict_legacy[value]}", LEGACY_API=f"Value for {key} is {key_val_dict[key]}")
                else:
                    obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"Check if values are not equal.",status.PASS, CURRENT_API=f"Value for {key} is {key_val_dict[key]}", LEGACY_API=f"Value for {value} is {key_val_dict_legacy[value]}")
            else:
                if 'legacy' in key:
                    obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"Check if values are not equal.",status.FAIL, CURRENT_API=f"Value for {value} is {key_val_dict_legacy[value]}", LEGACY_API=f"Value for {key} is {key_val_dict[key]}")
                else:
                    obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"Check if values are not equal.",status.FAIL, CURRENT_API=f"Value for {key} is {key_val_dict[key]}", LEGACY_API="")
                    obj.addMisc("REASON OF FAILURE", "Mismatches found during Assertion")
    except:
        traceback.print_exc()

            
    

def compareNotTo(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """checks for inequality of actual value and expected value. 
    OPERATOR -"notto, not_to"
    """
    
    actual_value = key_val_dict.get(key, key)
    if isinstance(actual_value, (int, float)):
        actual_value = str(actual_value)
        exp_value = str(value.strip('"').strip("'"))
    else:
        actual_value = str(actual_value).lower()
        exp_value = value.strip('"').strip("'").lower()

    if actual_value != exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = Not To",status.PASS, CURRENT_API = "-",LEGACY_API = f"Expected:-- != {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied" )
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = Not To",status.PASS, CURRENT_API=f"Expected:-- {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- != {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = Not To",status.FAIL, CURRENT_API="-",LEGACY_API = f"Expected:-- != {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied" )
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = Not To",status.FAIL, CURRENT_API=f"Expected:-- != {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- != {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied", status.FAIL)
            obj.addMisc("REASON OF FAILURE", "Mismatches found during Assertion")
    
    return obj


def compareIn(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """Checks whether the actual value is in the list of expecteds value or not
    OPERATOR - "in"
    """
    actual_value = key_val_dict.get(key, key)

    exp_value = [i.strip('"').strip("'").lower() for i in list(value.strip("[]").split(","))]
    if isinstance(actual_value, (int, float)):
        actual_value = actual_value
        try:
            exp_value = [float(i) for i in exp_value]
        except Exception as e:
            logging.info(str(e)) 
    else:
        actual_value = str(actual_value).lower()
    if actual_value in exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}" ,f"Operator = in", status.PASS, CURRENT_API = "-",LEGACY_API = f"Expected:-- in list {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied")
            else:
                obj.addRow(f"Running validation for {key}" ,f"Operator = in", status.PASS, CURRENT_API = f"Expected:-- in list {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied",LEGACY_API = "-")
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- in list {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = in", status.FAIL,CURRENT_API="-", LEGACY_API=f"Expected:-- in list {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied")
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = in", status.FAIL,CURRENT_API=f"Expected:-- in list {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- in list {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied", status.FAIL)
            obj.addMisc("REASON OF FAILURE", "Mismatches found during Assertion")
    

    return obj


def compareNotIn(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """Checks whether the actual value is absent from the not expected values or not.
    OPERATOR - "notin, not_in"
    """
    actual_value = key_val_dict.get(key, key)

    exp_value = [i.strip('"').strip("'").lower() for i in list(value.strip("[]").split(","))]

    if isinstance(actual_value, (int, float)):
        actual_value = actual_value
        try:
            exp_value = [float(i) for i in exp_value]
        except Exception as e:
            logging.info(str(e))
    else:
        actual_value = str(actual_value).lower()
        exp_value = value.strip('"').strip("'").lower()
    if actual_value not in exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = not in",status.PASS,CURRENT_API="-", LEGACY_API=f"Expected:-- not in list {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied")
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = not in",status.PASS,CURRENT_API=f"Expected:-- not in list {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- not in list {str(exp_value)}Actual:-- {str(actual_value)}condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = not in",status.FAIL,CURRENT_API="-", LEGACY_API=f"Expected:-- not in list {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied")
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = not in",status.FAIL,CURRENT_API=f"Expected:-- not in list {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- not in list {str(exp_value)}Actual:-- {str(actual_value)}condition not satisfied", status.FAIL)
            obj.addMisc("REASON OF FAILURE", "Mismatches found during Assertion")
        
    return obj

def compareContains(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """Checks whether the actual value contains(substring) expected value or not
    OPERATOR - "contains"
    """
    actual_value = key_val_dict.get(key, key)
    if value.lower().strip("'").strip('"') in str(actual_value).strip("'").strip('"').lower():
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = contains",status.PASS, CURRENT_API="-", LEGACY_API=f"Expected:-- contains {value}Actual:-- {str(actual_value)}condition satisfied")
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = contains",status.PASS, CURRENT_API=f"Expected:-- contains {value}Actual:-- {str(actual_value)}condition satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- contains {value}Actual:-- {str(actual_value)}condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow(f"Running validation for {key}",f"Operator = contains", status.FAIL, CURRENT_API="-", LEGACY_API=f"Expected:-- contains {value}Actual:-- {str(actual_value)}condition not satisfied")
            else:
                obj.addRow(f"Running validation for {key}",f"Operator = contains", status.FAIL, CURRENT_API=f"Expected:-- contains {value}Actual:-- {str(actual_value)}condition not satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"Expected:-- contains {value}Actual:-- {str(actual_value)}condition not satisfied", status.FAIL)
            obj.addMisc("REASON OF FAILURE", "Mismatches found during Assertion")
        
    return obj


def noOperator(obj):
    logging.info("operator not supported")
    return obj
