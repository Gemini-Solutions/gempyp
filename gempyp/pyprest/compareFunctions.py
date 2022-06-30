from gempyp.libs.enums.status import status
import logging as logger


##   check if actual value is sring or not

def compare_to(obj, key, value, key_val_dict, tolerance=0.1):
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

        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "


    return obj


def compare_notto(obj, key, value, key_val_dict, tolerance=0.1):
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
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> != {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
    
    return obj


def compare_in(obj, key, value, key_val_dict, tolerance=0.1):
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
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
    

    return obj


def compare_notin(obj, key, value, key_val_dict, tolerance=0.1):
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
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> not in list {str(exp_value)}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
        
    return obj

def compare_contains(obj, key, value, key_val_dict, tolerance=0.1):
    """Checks whether the actual value contains(substring) expected value or not
    OPERATOR - "contains"
    """
    actual_value = key_val_dict.get(key, key)
    if value.lower().strip("'").strip('"') in str(actual_value).strip("'").strip('"').lower():

        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition satisfied", status.PASS)
    else:
        obj.addRow(f"Running validation for {key}", f"<b>Expected:--</b> contains {value}</br><b>Actual:--</b> {str(actual_value)}</br>condition not satisfied", status.FAIL)
        obj._miscData["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
        
    return obj


def no_operator(obj):
    logger.info("operator not supported")
    return obj