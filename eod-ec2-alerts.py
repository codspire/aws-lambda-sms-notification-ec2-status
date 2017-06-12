# Personal SMS/Text Alert to show the count of running EC2 instances
# Author: Rakesh Nagar

import os
import boto3

print('Loading function')

def lambda_handler(event, context):
    TOPIC_ARN = os.environ['TOPIC_ARN']
    ec2Client = boto3.client('ec2')
    
    response = ec2Client.describe_instances(
		Filters=[
				{
					'Name': 'instance-state-name',
					'Values': [
						'pending',
						'running'
					]
				},
			],
    )
    
    instances = dict()
    
    for r in response['Reservations']:
    	for i in r['Instances']:
    		instanceType = i['InstanceType']
    		if instanceType in instances:
    			instances[instanceType] += 1
    		else:
    			instances[instanceType] = 1
    
    if len(instances) > 0:
        msg = "%s active instance(s)\n" %(len(instances))
        for k in sorted(instances, reverse=True):	
            msg = "%s %s - %s\n" %(msg,instances[k],k)
        
        print(msg)
        
        snsClient = boto3.client('sns')
        snsResponse = snsClient.publish(
    		TopicArn=TOPIC_ARN,
    		Message=msg
    	)
        print(snsResponse)
    else:
    	print("No instance is running")    

# Enable execution of Lambda functionally from local machine
# Note: export the TOPIC_ARN environment variable before running this function
if __name__ == "__main__":
    event = []
    context = []
    lambda_handler(event, context)
