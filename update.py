import clamav
import yarascan
from common import *
from datetime import datetime
import os


def lambda_handler(event, context):
    start_time = datetime.utcnow()
    print("Script starting at %s\n" %
          (start_time.strftime("%Y/%m/%d %H:%M:%S UTC")))
    clamav.update_defs_from_s3(AV_DEFINITION_S3_BUCKET, AV_DEFINITION_S3_PREFIX)
    clamav.update_defs_from_freshclam(AV_DEFINITION_PATH, CLAMAVLIB_PATH)
    yarascan.update_sigs_from_s3(YARA_RULES_S3_BUCKET, YARA_RULES_S3_PREFIX)
    # If main.cvd gets updated (very rare), we will need to force freshclam
    # to download the compressed version to keep file sizes down.
    # The existence of main.cud is the trigger to know this has happened.
    if os.path.exists(os.path.join(AV_DEFINITION_PATH, "main.cud")):
        os.remove(os.path.join(AV_DEFINITION_PATH, "main.cud"))
        if os.path.exists(os.path.join(AV_DEFINITION_PATH, "main.cvd")):
            os.remove(os.path.join(AV_DEFINITION_PATH, "main.cvd"))
        clamav.update_defs_from_freshclam(AV_DEFINITION_PATH, CLAMAVLIB_PATH)
    clamav.upload_defs_to_s3(AV_DEFINITION_S3_BUCKET, AV_DEFINITION_S3_PREFIX, AV_DEFINITION_PATH)
    print("Script finished at %s\n" %
          datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S UTC"))
