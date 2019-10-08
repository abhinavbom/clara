# clara
ClamAV+Yara scanning your S3 Buckets

## What is clara
Clara is Python based project used to scan your S3 bucket files with ClamAV and Yara signatures.
It is built on top of Upside Travel's bucket-antivirus-function project and extends it to following improvements:
* Yara Scanning feature with signature updates.
* Python 3.7 support.

## Setup:

### Step 1: Building the Lambda Zip file from source

change current directory to clara and run `make`
This will create a Build directory with the zip file containing the lambda fuction code and requirements. 

### Step 2: Creating the S3 buckets.

We will need three different S3 buckets for this project. One for storing the files to be scanned, second for storing clamAV definitions and third for storing your Yara rules. 

1. Create an S3 bucket with named ```file-scanning-upload```. This bucket will hold the files to be scanned by clara. 


2. Create  a second bucket to store the clamAV definitions. Name the bucket as ```clamav-definition-updates```.

3. Upload the most recent defintion files [main.cvd](http://database.clamav.net/main.cvd), [daily.cvd](http://database.clamav.net/daily.cvd) and [bytecode.cvd](http://database.clamav.net/bytecode.cvd) to this bucket. 

4. For this same bucket, navigate to Permissions Tab and select Bucket Policy. Copy and paste the json policy from ```clamav-definition-updates-policy.json``` to this field and save. This policy gives public access to the bucket allowing it to download definitions from the internet. 

5. Now, create the third and final bucket and name it ```yara-rule-updates```.

6. You can now upload your yara signature sets to this bucket. Once done, again navigate to Permissions tab and select Bucket Policy. Copy and paste the json policy defined in ```yara-rule-updates-policy.json``` here. 

Now we are all set with creating our S3 buckets and assigning the required access policies. 


### Step 3: 
