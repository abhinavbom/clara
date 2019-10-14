# 06/23/2019 - Adding new feature to update bucket containing Rara rules for scanning.
#author: Abhinav Singh


import hashlib
import os
import pwd
import re
from common import *
from subprocess import check_output, Popen, PIPE, STDOUT
import yara
import logging
import boto3

def current_library_search_path():
    ld_verbose = check_output(["ld", "--verbose"]).decode('utf-8')
    rd_ld = re.compile("SEARCH_DIR\(\"([A-z0-9/-]*)\"\)")
    return rd_ld.findall(ld_verbose)


def update_sigs_from_s3(bucket, prefix):
    create_dir(YARA_DEFINITION_PATH)
    print ("created yara definitions directory %s" %YARA_DEFINITION_PATH)
    #initiate s3 resource
    s3 = boto3.resource('s3')
    # select bucket
    my_bucket = s3.Bucket(YARA_RULES_S3_BUCKET)
    local_path = YARA_DEFINITION_PATH
    # download file into current directory
    for s3_object in my_bucket.objects.all():
        # Need to split s3_object.key into path and file name, else it will give error file not found.
        path, filename = os.path.split(s3_object.key)
        local_path = os.path.join(YARA_DEFINITION_PATH, filename)
        print ("downloading yara rules")
        print(path, filename)
        my_bucket.download_file(s3_object.key, local_path)

def scan_file(path):
    pwd = os.getcwd()
    print (pwd)
    #YARA_DEFINITION_PATH = pwd+'/yara_rules/'
    file_list = []
    rule_name_list = []
    yara_scan_info = {
        "scan_performed":"No",
        "scan_result" : "Not-detected",
        "detection_rule" : "N/A",
        "clamAV_scan": "N/A"
        }
    yara_env = os.environ.copy()
    yara_env["LD_LIBRARY_PATH"] = YARA_LIB_PATH
    #print(yara_env)
    file = open(path,'rb') #open file for yara scanning
    print (file)
    file_data = file.read()
    try:
        for (dirpath, dirnames, filenames) in os.walk(YARA_DEFINITION_PATH):
            file_list.extend(filenames)
            print (file_list)
        for item in file_list:
            #print (file_list)
            rule = yara.compile(filepath= YARA_DEFINITION_PATH+ '/' + str(item))
            matches = rule.match(data=file_data)
            logging.info(matches)
            if matches:
                rule_name_list.append(matches[0].rule)
                yara_scan_info['scan_performed']="Yes"
                yara_scan_info['scan_result']="Detected"
                yara_scan_info['detection_rule'] = rule_name_list
        print (yara_scan_info)
    except Exception as e:
        print (e)

def main():
    path = input("Enter the path of your file: ")
    scan_file(path)

if __name__ == "__main__":
    main()
    
