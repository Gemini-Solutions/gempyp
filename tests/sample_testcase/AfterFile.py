import os.path

def check():
    file_str="path=C:\\Users\\ta.agarwal\\gempyp\\tests\\sample_testcase\\testcase,class=body"
    file_name=file_str.split("path=")[1].split(',')[0]
    if(os.path.isabs(file_name)):
        print(file_name.split("\\")[-1])
if __name__ == "__main__":
    check()

        