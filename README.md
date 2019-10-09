# Clara
Serverless, real-time, ClamAV+Yara scanning for your S3 Buckets

## What is clara
Clara is Python based project used to scan your S3 bucket files with ClamAV and Yara signatures.
It is built on top of Upside Travel's [bucket-antivirus-function](https://github.com/upsidetravel/bucket-antivirus-function) project and Airbnb's (BinaryAlert)[https://github.com/airbnb/binaryalert] project. *Clara* combines the two functionalities into a single project with some additional improvements:
* Yara and ClamAV Scanning feature with signature updates.
* Slack/Email SNS alerts.
* DynamoDB storage support.
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

2. Name the function as ```bucket-defs-update``` and select the runtime as **Python 3.7**.

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
* Creating the scanner lambda function

1. Create a new lambda function and name it as ```bucket-scanner-function```. Select the runtime environment as **Python 3.7**.

2. In the Designer tab, add a new trigger and select **S3 Event**. 

3. Select your bucket name where the scanning files will be uploaded. In this example we have named it as ```file-scanning-upload```. In the **Event Type** select **All object create event**. Make sure that enable trigger is configured. Then click on Add. 

4. In the **Function code** section slect the zip file created in Step 1. Set Python3.7 as the runtime environment. Set the value of **Handler** as ```scan.lambda_handler```. 

5. Define the below two environment variable key values: 
AV_DEFINITION_S3_BUCKET     clamav-definition-updates
YARA_RULES_S3_BUCKET        yara-rule-updates

6. For the **Execution Role**, create a new role and name it as ```bucket-scanner-function```. Select **Attach Policy** and create a new policy. You can again name the policy as above. Copy-paste the ```bucket-scanner-function-policy.json``` into the JSON editor of the policy and save it. 

7. Go back to the lambda function creation dashboard. In the **Execution role**, select **use an existing role** and choose the newly created role. 

8. In the **Basic settings**, set the memory to 2048MB and timeout as 3 minutes. Save the lambda function. 

## Step 5

### Testing the Lambda functions

1. Click on Test functions and let it run with the default values. 

2. Come back to your lambda function page. You should now have two functions created. Click on the ```bucket-defs-update``` function to launch its UI. Select the monitoring tab and you should see the graph with execution of test event details. 

3. You can click on **View Logs in CloudWatch** to see the log lines created by the lambda function. You should see print lines about definitions and rules getting updated. 

2. Go to your S3 bucket ```file-scanning-upload``` and add a new file there. 

3. Now, open the monitoring page of the ```bucket-scanner-function```. Select **View logs in CloudWatch**. You should see the scanning getting initiated. If there is a detection, it should print in the log line. 


## Acknowledgements

* [Bucket-antivirus-fuction](https://github.com/upsidetravel/bucket-antivirus-function)
* [Binary Alert](https://github.com/airbnb/binaryalert)
