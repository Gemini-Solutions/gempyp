from gempyp.libs.enums.status import status
import logging as logger


##   check if actual value is sring or not

def compare_to(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """checks for equality of actual value and expected value. 
    OPERATOR -"to"
    """
    actual_value = key_val_dict.get(key, key)
    if isinstance(actual_value, (int, float)):
        actual_value = actual_value
        exp_value = float(value.strip('"').strip("'").lower()) 
    else:
        actual_value = str(actual_value).lower()
        exp_value = value.strip('"').strip("'").lower()
        
    if actual_value == exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = To</b>",status.PASS, CURRENT_API = "-",LEGACY_API = f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied" )
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = To</b>",status.PASS, CURRENT_API=f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = To</b>",status.FAIL, CURRENT_API="-",LEGACY_API = f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied" )
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = To</b>",status.FAIL, CURRENT_API=f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "


    return obj


def compare_to_resp(obj,key,value, key_val_dict, key_val_dict_legacy, tolerance):
    actual_value = key_val_dict.get(key,key)
    required_value = key_val_dict_legacy[value]
    if actual_value == required_value:
        if 'legacy' in key:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<br> <b>check values are equal </b>",status.PASS, CURRENT_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>", LEGACY_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>")
        else:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are equal </b>",status.PASS, CURRENT_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>", LEGACY_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>")
    else:
        if 'legacy' in key:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are equal </b>",status.FAIL, CURRENT_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>", LEGACY_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>")
        else:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are equal </b>",status.FAIL, CURRENT_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>", LEGACY_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>")

def compare_notto_resp(obj,key,value, key_val_dict, key_val_dict_legacy, tolerance):
    actual_value = key_val_dict.get(key,key)
    required_value = key_val_dict_legacy[value]
    if actual_value != required_value:
        if 'legacy' in key:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are not equal.</b>",status.PASS, CURRENT_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>", LEGACY_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>")
        else:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are not equal.</b>",status.PASS, CURRENT_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>", LEGACY_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>")
    else:
        if 'legacy' in key:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are not equal.</b>",status.FAIL, CURRENT_API=f"Value for <b>{value}</b> is <b>{key_val_dict_legacy[value]}</b>", LEGACY_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>")
        else:
            obj.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"<b>check values are not equal.</b>",status.FAIL, CURRENT_API=f"Value for <b>{key}</b> is <b>{key_val_dict[key]}</b>", LEGACY_API="")


def compare_notto(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """checks for inequality of actual value and expected value. 
    OPERATOR -"notto, not_to"
    """
    
    actual_value = key_val_dict.get(key, key)
    if isinstance(actual_value, (int, float)):
        actual_value = actual_value
        exp_value = float(value.strip('"').strip("'").lower()) 
    else:
        actual_value = str(actual_value).lower()
        exp_value = value.strip('"').strip("'").lower()

    if actual_value != exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = Not To</b>",status.PASS, CURRENT_API = "-",LEGACY_API = f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied" )
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = Not To</b>",status.PASS, CURRENT_API=f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = Not To</b>",status.FAIL, CURRENT_API="-",LEGACY_API = f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied" )
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = Not To</b>",status.FAIL, CURRENT_API=f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied",LEGACY_API="-" )
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
    
    return obj


def compare_in(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
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
            print(str(e)) 
    else:
        actual_value = str(actual_value).lower()
    if actual_value in exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion", f"Running validation for <b>{key}</b>, <b>Operator = in</b>", status.PASS, CURRENT_API = "-",LEGACY_API = f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied")
            else:
                obj.addRow("Execution of post assertion", f"Running validation for <b>{key}</b>, <b>Operator = in</b>", status.PASS, CURRENT_API = f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied",LEGACY_API = "-")
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = in</b>", status.FAIL,CURRENT_API="-", LEGACY_API=f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied")
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = in</b>", status.FAIL,CURRENT_API=f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
    

    return obj


def compare_notin(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
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
            print(str(e))
    else:
        actual_value = str(actual_value).lower()
        exp_value = value.strip('"').strip("'").lower()
    if actual_value not in exp_value:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = not in</b>",status.PASS,CURRENT_API="-", LEGACY_API=f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied")
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = not in</b>",status.PASS,CURRENT_API=f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = not in</b>",status.FAIL,CURRENT_API="-", LEGACY_API=f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied")
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = not in</b>",status.FAIL,CURRENT_API=f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
        
    return obj

def compare_contains(obj, key, value, key_val_dict, tolerance=0.1, isLegacyPresent = False, isLegacyResponse = False):
    """Checks whether the actual value contains(substring) expected value or not
    OPERATOR - "contains"
    """
    actual_value = key_val_dict.get(key, key)
    if value.lower().strip("'").strip('"') in str(actual_value).strip("'").strip('"').lower():
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = contains</b>",status.PASS, CURRENT_API="-", LEGACY_API=f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied")
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = contains</b>",status.PASS, CURRENT_API=f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        if isLegacyPresent:
            if isLegacyResponse:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = contains</b>", status.FAIL, CURRENT_API="-", LEGACY_API=f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied")
            else:
                obj.addRow("Execution of post assertion",f"Running validation for <b>{key}</b>, <b>Operator = contains</b>", status.FAIL, CURRENT_API=f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", LEGACY_API="-")
        else:
            obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
        
    return obj


def no_operator(obj):
    logger.info("operator not supported")
    return obj