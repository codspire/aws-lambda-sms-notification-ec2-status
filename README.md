# Send SMS alert with count & type of running EC2 instances

I created this lambda function to send me the count and type of EC2 instances running in my account *(Yes, I'm burnt few times by unused EMR clusters).

Below is how it works:

CloudWatch Scheduled Event -> Lambda -> SNS Topic -> Mobile

Steps

## 1: Create a SNS Topic

```sh
$ aws sns create-topic --name "eod-ec2-alerts" --output text --query TopicArn
```

Note down the `TopicArn`

## 2: Create Subscription to receive SMS

* Substitute `<TopicArn>` with topic arn created in previous step
* Substitute `<MobileNumber>` Mobile number for SMS alerts (format 12223334444)

```sh
$ aws sns subscribe --topic-arn <TopicArn> --protocol sms --notification-endpoint <MobileNumber>
```
  
Set display name for the topic

* Substitute `<TopicArn>` with topic arn

```sh
$ aws sns set-topic-attributes --topic-arn <TopicArn> --attribute-name DisplayName --attribute-value "AWS Alert"
```

## 3: Create Lambda Execution Role & Policies

```sh
$ aws iam create-role \
  --role-name "lambda-eod-ec2-alerts-execution" \
  --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "sts",
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }' \
  --output text \
  --query 'Role.Arn'
```

Note down the `Role.Arn`

Policies to allow lambda to communicate with SNS & EC2
Instead of hard coding the topic arn in the lambda function we can externalize it as environment variable. AWS encrypts the environment variables therefore we need to pass the custom key managed through KMS

* Substitute `<TopicArn>` with the topic arn
* Substitute `<KMSKeyArn>` with the key arn managed through KMS

If you don't want to use the KMS, you can skip the KMS policy snippet below and specify the topic arn in the Lambda code (TOPIC_ARN)
  
```sh
$ aws iam put-role-policy \
  --role-name "lambda-eod-ec2-alerts-execution" \
  --policy-name "lambda-eod-ec2-alerts-execution-access" \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:Describe*"
        ],
        "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "sns:Publish"
        ],
        "Resource": <TopicArn>
      },
      {
	"Effect": "Allow",
	"Action": [
	  "kms:Encrypt",
	  "kms:Decrypt"
	],
	"Resource":<KMSKeyArn>
       }
    ]
  }'
  ```
## 4: Create Lambda Function

Package the code in zip file
```sh
$ zip eod-ec2-alerts.zip eod-ec2-alerts.py
```

* Substitute `<RoleArn>` with the role arn
* Substitute `<TopicArn>` with the topic arn
* Substitute `<KMSKeyArn>` with the key arn managed through KMS

```sh
$ aws lambda create-function \
  --function-name "eod-ec2-alerts" \
  --zip-file "fileb://eod-ec2-alerts.zip" \
  --role <RoleArn> \
  --handler "eod-ec2-alerts.lambda_handler" \
  --environment '{"Variables":{"TOPIC_ARN":<TopicArn>}}' \
  --timeout 30 \
  --runtime python3.6 \
  --description "Check the status of services at EOD" \
  --kms-key-arn <KMSKeyArn> \
  --region us-east-1
```

Use below command to create lambda if  you don't want to use KMS. Make sure to specify the topic arn in the lambda code

```sh
$ aws lambda create-function \
  --function-name "eod-ec2-alerts" \
  --zip-file "fileb://eod-ec2-alerts.zip" \
  --role <RoleArn> \
  --handler "eod-ec2-alerts.lambda_handler" \
  --timeout 30 \
  --runtime python3.6 \
  --description "Check the status of services at EOD" \
  --region us-east-1
```

## 5: Test The Lambda Function
```sh
$ aws lambda invoke --function-name eod-ec2-alerts outfile.txt
```
Link the lambda with other events or schedule the CloudWatch event to run it periodically

