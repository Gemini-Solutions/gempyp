from gempyp.libs.enums.status import status
import os, uuid, logging
from gempyp.libs.common import download_common_file,get_reason_of_failure
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link
import traceback
from gempyp.config import DefaultSettings
from gempyp.dv.dvObj import DvObj
from gempyp.libs.common import moduleImports

def writeExcel(df, keys_length, reporter,configData):

    try:
        reporter.logger.info("----------in write excel---------")
        reporter.logger.info("In write Excel Function")

        outputFolder = configData.get('REPORT_LOCATION',os.getcwd())
        unique_id = uuid.uuid4()
        excelPath = os.path.join(
            outputFolder, configData.get('NAME','dv')+str(unique_id)+'.csv')
        excel = os.path.join(
            ".", "testcases", configData.get('NAME','dv')+str(unique_id)+'.csv')
        if "AFTER_FILE" in configData:
            df, reporter = afterMethod(df,reporter,configData)
        if (keys_length.get("key_check",0) + keys_length.get("value_check",0) + keys_length.get("dup_keys_len",0)) == 0:
            reporter.addRow("Data Validation Report",
                                "No MisMatch Value Found", status=status.PASS)
            reporter.logger.info("----No MisMatch Value Found----")
        else:
            reporter.logger.info("----Adding Data to Excel----")
            # with pd.ExcelWriter(excelPath) as writer1:
                # if key_check == 0:
                #     pass
                # else:
                #     self.keys_df.to_excel(
                #         writer1, sheet_name='key_difference', index=False)
                # if value_check == 0:
                #     pass
                # else:
                #     self.value_df.to_excel(
                #         writer1, sheet_name='value_difference', index=False)
            # df = pd.concat([self.value_df, self.keys_df, duplicate_keys_df ], axis=0, ignore_index=True)
            df_columns = set(df.columns)
            fixed_columns = {"Column-Name","Source-Value","Target-Value","Reason-of-Failure"}
            diff_columns = df_columns - fixed_columns
            new_order = list(diff_columns)+["Column-Name","Source-Value","Target-Value","Reason-of-Failure"]
            df = df[new_order]
            df.to_csv(excelPath, index=False,header=True)
            s3_url = None
            
            """fetching username and bridgetoken from env variables"""
            
            username = os.environ.get('jewel-user',configData.get('USERNAME'))
            bridge_token = os.environ.get('jewel-bridge-token',configData.get('BRIDGE_TOKEN'))
            
            
            reporter.logger.info("trying to upload result file ")
            try:
                s3_url = create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"], bridge_token=bridge_token, tag="public", username=username, file=excelPath)[0]["Url"])
            except Exception as e:
                logging.warn(e)
            if not s3_url:
                reporter.addRow("Data Validation Report", f"Matched Keys: {keys_length['common_keys']}, Keys only in Source: {keys_length['keys_only_in_src']}, Keys only in Target: {keys_length['keys_only_in_tgt']}, Mismatched Cells: {keys_length['value_check']}, Duplicate Keys: {keys_length.get('dup_keys_length',0)}, DV Result File:", status=status.FAIL,Attachment=[excelPath])
            else:
                reporter.addRow("Data Validation Report", "Following Result Found", status=status.FAIL,Stats=[f"Matched Keys: {keys_length.get('common_keys',0)}, Keys only in Source: {keys_length.get('keys_only_in_src',0)}, Keys only in Target: {keys_length.get('keys_only_in_tgt',0)}, Mismatched Cells: {keys_length.get('value_check',0)}, Duplicate Keys: {keys_length.get('dup_keys_length',0)}"],Attachment=[s3_url])

            reporter.addMisc("REASON OF FAILURE", str(
                f"Mismatched Keys: {keys_length.get('key_check',0)},Mismatched Cells: {keys_length.get('value_check',0)}"))
        reporter.addMisc("common Keys", str(keys_length['common_keys']))
        reporter.addMisc("Keys Only in Source",
                            str(keys_length['keys_only_in_src']))
        reporter.addMisc("Keys Only In Target",
                            str(keys_length['keys_only_in_tgt']))
        reporter.addMisc("Mismatched Cells", str(keys_length.get("key_check",0)))
    except Exception as e:
        traceback.print_exc()
        reporter.addMisc(
                "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
        reporter.addRow("Writing Data into CSV","Exception Occurred",status.ERR)


def afterMethod(value_df,reporter,configData):
    """This function
    -checks for the after file tag
    -stores package, module,class and method
    -runs after method if found
    -takes all the data from after method and updates the self object"""

    reporter.logger.info("CHECKING FOR AFTER FILE___________________________")

    file_str = configData.get("AFTER_FILE", "")
    if not file_str or file_str == "" or file_str == " ":
        reporter.logger.info("AFTER FILE NOT FOUND___________________________")
        reporter.reporter.addRow(
            "Searching for After_File Steps", "No File Path Found", status.INFO)
        return value_df, reporter 

    reporter.addRow("Searching for After_File",
                            "Searching for File", status.INFO)

    file_name = file_str.split("path=")[1].split(",")[0]
    if "CLASS=" in file_str.upper():
        class_name = file_str.split("class=")[1].split(",")[0]
    else:
        class_name = ""
    if "METHOD=" in file_str.upper():
        method_name = file_str.split("method=")[1].split(",")[0]
    else:
        method_name = "after"
    reporter.logger.info("After file path:- " + file_name)
    reporter.logger.info("After file class:- " + class_name)
    reporter.logger.info("After file method:- " + method_name)
    try:
        file_path = download_common_file(
            file_name, configData.get("SUITE_VARS", None))
        file_obj = moduleImports(file_path)
        reporter.logger.info("Running After method")
        obj_ = file_obj
        after_obj = DvObj(
        
            mismatch_df=value_df,
            reporter=reporter 
        )
        if class_name != "":
            obj_ = getattr(file_obj, class_name)()
        fin_obj = getattr(obj_, method_name)(after_obj)
        df,reporter = extractAfterObj(fin_obj)
        return df,reporter
    except Exception as e:
        reporter.addRow(
            "Executing After method", f"Some error occurred while searching for after method- {str(e)}", status.ERR)
        return value_df, reporter


def extractAfterObj(obj):

    reporter = obj.reporter
    df = obj.mismatch_df
    return df, reporter
