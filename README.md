# Send type and count of running EC2 instances through SMS

I created this lambda function to send me the count and type of EC2 instances running in my account (Yes, I was burnt by leaving an EMR running after the use). 

Below is how this works:

CloudWatch Scheduled Event -> Lambda -> SNS Topic -> Mobile


Steps:
