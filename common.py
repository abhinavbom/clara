import boto3
import errno
import os

AV_DEFINITION_S3_BUCKET = os.getenv("AV_DEFINITION_S3_BUCKET")
AV_DEFINITION_S3_PREFIX = os.getenv("AV_DEFINITION_S3_PREFIX", "clamav_defs")
AV_DEFINITION_PATH = os.getenv("AV_DEFINITION_PATH", "/tmp/clamav_defs")
AV_SCAN_START_SNS_ARN = os.getenv("AV_SCAN_START_SNS_ARN")
AV_SCAN_START_METADATA = os.getenv("AV_SCAN_START_METADATA", "av-scan-start")
AV_STATUS_CLEAN = os.getenv("AV_STATUS_CLEAN", "CLEAN")
AV_STATUS_INFECTED = os.getenv("AV_STATUS_INFECTED", "INFECTED")
AV_STATUS_METADATA = os.getenv("AV_STATUS_METADATA", "av-status")
AV_STATUS_SNS_ARN = os.getenv("AV_STATUS_SNS_ARN")
AV_TIMESTAMP_METADATA = os.getenv("AV_TIMESTAMP_METADATA", "av-timestamp")
CLAMAVLIB_PATH = os.getenv("CLAMAVLIB_PATH", "./bin")
CLAMSCAN_PATH = os.getenv("CLAMSCAN_PATH", "./bin/clamscan")
FRESHCLAM_PATH = os.getenv("FRESHCLAM_PATH", "./bin/freshclam")
AV_PROCESS_ORIGINAL_VERSION_ONLY = os.getenv("AV_PROCESS_ORIGINAL_VERSION_ONLY", "False")
AV_DELETE_INFECTED_FILES = os.getenv("AV_DELETE_INFECTED_FILES", "False")
YARA_RULES_S3_BUCKET = os.getenv("YARA_RULES_S3_BUCKET")
YARA_RULES_S3_PREFIX = os.getenv("YARA_RULES_S3_PREFIX", "yara_rules")
YARA_DEFINITION_PATH = os.getenv("YARA_DEFINITION_PATH", "/tmp/yara_rules")
YARA_LIB_PATH = os.getenv("YARA_LIB_PATH", "./bin")
YARASCAN_PATH = os.getenv("YARASCAN_PATH", "./bin/yara")
AV_DEFINITION_FILENAMES = ["main.cvd", "daily.cvd", "daily.cud", "bytecode.cvd", "bytecode.cud"]

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def create_dir(path):
    if not os.path.exists(path):
        try:
            print("Attempting to create directory %s.\n" % path)
            os.makedirs(path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
