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
* Creating the rules and definition update Lambda function

1. Proceed to your AWS Lambda dashboard UI and create a new lambda fuction. Select "From scratch" to define our own parameters. 

2. Name the function as ```bucket-defs-update``` and select the runtime as ```Python 3.7```.

3. In the Designer tab, click on the left side "Add trigger" option. Select ```CloudWatch Events``` and then add ```rate(3 hours)``` for **Scheduled expression**. Make sure that **enable trigger** option is selected. Save it. 

4. In the Function code section, select "upload from zip file" and select the Build.zip file that we created in step 1. Again, select the runtime as Python 3.7. In the Handler field add ```update.lambda_handler```.

5. In the environment variables field, we will have to provide the bucket names where our ClamAV and Yara rules recide. Define the following key and value in this field: 
Key                             Value
AV_DEFINITION_S3_BUCKET         clamav-definition-updates
YARA_RULES_S3_BUCKET            yara-rule-updates

6. For the Execution role section, we will have to create a new role to be attached to our lambda function. Head to your IAM dashboard, Click on "Roles" and "create new role". 
    i. Name your role as ```bucket-defs-update```. 
    ii. Click on "Attach policies" and then create a new policy. 
    iii. Copy-paste the json policy from ```bucket-defs-update-policy.json``` and save it. Once the policy is attached to the role, go back to your Lambda creation page and scroll to the "Execution Role" section.

7. In the "Execution role" section, select "Use an existing role" and select the newly created role. You might want to click on the Refresh button for your role to reflect. 

8. In the "Basic Settings", select 512MB memory and Timout as 3 minutes. 

9. (Optional) Choose the VPC where you want to add your lambda function.


## Step 4
* AWS scanner lambda 