# Send type and count of running EC2 instances through SMS

I created this lambda function to send me the count and type of EC2 instances running in my account (Yes, I was burnt by leaving an EMR running after the use). 

Below is how it works:

CloudWatch Scheduled Event -> Lambda -> SNS Topic -> Mobile

Steps

1: Create a SNS Topic

```sh
aws sns create-topic --name "eod-ec2-alerts" --output text --query TopicArn
```

Note down the Topic ARN

2: Create Subscription to receive SMS

```sh
aws sns subscribe --topic-arn <TopicArn> --protocol sms --notification-endpoint <MobileNumber>
```
  <TopicArn> with topic arn created in previous step
  <MobileNumber> Mobile number for SMS alerts (format 12223334444)
  
Set display name for the topic

```sh
aws sns set-topic-attributes --topic-arn <TopicArn> --attribute-name DisplayName --attribute-value "AWS Alert"
```

2: Create Lambda Execution Role & Policies

```sh
aws iam create-role \
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

Note down the Role ARN


```sh
aws iam put-role-policy \
  --role-name "$lambda_execution_role_name" \
  --policy-name "$lambda_execution_access_policy_name" \
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
        "Resource": ${topic_arn}
      },
	{
		"Effect": "Allow",
		"Action": [
		  "kms:Encrypt",
		  "kms:Decrypt"
		],
		"Resource":${kms_key_arn}
	}
    ]
  }'
  ```
