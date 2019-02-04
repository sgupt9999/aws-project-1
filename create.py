#!/usr/local/bin/python3.6

# This program will create a new VPC, RDS instance, Elastic Beanstalk envirnment and an S3 bucket

import boto3
import sys
import urllib.request
import shutil


def download_sample_files(sample_list):
# Download the sample platform code for elastic beanstalk
	for sample in sample_list:
		with urllib.request.urlopen(sample[1]) as response, open(sample[2], 'wb') as out_file:
			shutil.copyfileobj(response, out_file)

def upload_sample_files(sample_list,bucket_name):
# Upload the downloaded sample platform files to the new S3 bucket
	s3 = boto3.client('s3')
	for sample in sample_list:
		content = open(sample[2],'rb')
		s3.put_object(Bucket=bucket_name,Key=sample[2],Body=content)

########## User inputs ##################

vpc_stackname = 'mixedvpc2'
rds_stackname = 'rds'
profile_stackname = 'profile'
s3_stackname = 's3'
ebs_stackname = 'ebs'

## vpc stack parameters
basename = 'cmei'
privatesubnets = 'true'

## rds stack pareameters
dbsecurity = 'public' # Create either private or public DB
dbname = 'testdb'
dbusername = 'myadmin'
dbpassword = 'qpwoeiruty1000$'
deletionprotection = 'false'

## ebs stack parameters
applicationname = 'testapp'
environmentname = 'testapp-dev'
keyname = 'Oregon-1'
domain = 'cmeisystems.com.'
certid = 'arn:aws:acm:us-west-2:310471513752:certificate/0be5c56b-f510-43fc-bf29-088d8b03f072'
sampleappbucket = 'cmei-sample-applications-oregon'
# The following list has to match the mapping in the ebs stack definiton
samplecode = [['Java','https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/samples/java-se-jetty-gradle-v3.zip','java-se-jetty-gradle-v3.zip'],\
	      ['Node.js','https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/samples/nodejs-v1.zip','nodejs-v1.zip'],\
	      ['PHP','https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/samples/php-v1.zip','php-v1.zip'],\
	      ['Python','https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/samples/python-v1.zip','python-v1.zip']]


########## End of User inputs ##################


client = boto3.client('cloudformation')

## Create VPC stack
print('Creating vpc stack')
vpc_file = open('./cfn-vpc.yaml')
vpc_template = vpc_file.read()
response_vpc = client.create_stack(StackName=vpc_stackname,TemplateBody=vpc_template,Parameters=[{'ParameterKey':'BaseName','ParameterValue':basename},\
					{'ParameterKey':'PrivateSubnets','ParameterValue':privatesubnets}])
vpc_waiter = client.get_waiter('stack_create_complete')
try:
	vpc_waiter.wait(StackName = response_vpc['StackId'])
except:
	print('VPC Stack creation failed. Exiting the script')
	exit(1)
vpc = client.describe_stack_resources(StackName=vpc_stackname)
vpc_endpoints3 = client.describe_stack_resource(StackName=vpc_stackname,LogicalResourceId='VPCEndPointS3')['StackResourceDetail']['PhysicalResourceId']
print('VPC stack created successfully')

## Create 1st s3 stack
print('Creating S3 bucket to save the sample elasticbeanstalk platforms')
download_sample_files(samplecode)
s3_file = open('./cfn-s3.yaml')
s3_template = s3_file.read()
response_s3 = client.create_stack(StackName=s3_stackname,TemplateBody=s3_template)
s3_waiter = client.get_waiter('stack_create_complete')
try:
	s3_waiter.wait(StackName = response_s3['StackId'])
except:
	print('S3 Stack creation failed. Exiting the script')
	exit(1)
sample_codebucket = client.describe_stack_resource(StackName=s3_stackname,LogicalResourceId='S3')['StackResourceDetail']['PhysicalResourceId']
upload_sample_files(samplecode,sample_codebucket)
print('1st S3 stack created successfully')

## Create EC2 instance profile for Elastic BeanStalk
print('Creating EC2 instance profile for elastic beanstalk')
profile_file = open('./cfn-ec2-instance-profile.yaml')
profile_template = profile_file.read()
response_profile = client.create_stack(StackName=profile_stackname,TemplateBody=profile_template,Capabilities=['CAPABILITY_NAMED_IAM'])
profile_waiter = client.get_waiter('stack_create_complete')
try:
	profile_waiter.wait(StackName = response_profile['StackId'])
except:
	print('EC2 instance Stack creation failed. Exiting the script')
	exit(1)
#profile = client.describe_stack_resources(StackName=profile_stackname)
ec2ebs_profile = client.describe_stack_resource(StackName=profile_stackname,LogicalResourceId='EC2EBSProfile')['StackResourceDetail']['PhysicalResourceId']
print('EC2 instance profile stack created successfully')


## Create Elastic BeanStalk stack
print('Creating the elastic beanstalk stack')
ebs_file = open('./cfn-ebs.yaml')
ebs_template = ebs_file.read()
response_ebs = client.create_stack(StackName=ebs_stackname,TemplateBody=ebs_template,Parameters=[{'ParameterKey':'VPCStackName','ParameterValue':vpc_stackname},\
					{'ParameterKey':'ApplicationName','ParameterValue':applicationname},\
					{'ParameterKey':'EnvironmentName','ParameterValue':environmentname},\
					{'ParameterKey':'KeyName','ParameterValue':keyname},\
					{'ParameterKey':'Domain','ParameterValue':domain},\
					{'ParameterKey':'CertId','ParameterValue':certid},\
					{'ParameterKey':'EC2InstanceProfile','ParameterValue':ec2ebs_profile},\
					{'ParameterKey':'SampleApplicationBucket','ParameterValue':sample_codebucket}\
					])
ebs_waiter = client.get_waiter('stack_create_complete')
try:
	ebs_waiter.wait(StackName = response_ebs['StackId'])
except:
	print('Elastic Beanstalk Stack creation failed. Exiting the script')
	exit(1)
ebs = client.describe_stack_resources(StackName=ebs_stackname)
print('Elastic Beanstalk stack created successfully')
#print(ebs)

## Create RDS stack
print('Creating rds stack')
rds_file = open('./cfn-rds.yaml')
rds_template = rds_file.read()
response_rds = client.create_stack(StackName=rds_stackname,TemplateBody=rds_template,Parameters=[{'ParameterKey':'VPCStackName','ParameterValue':vpc_stackname},\
					{'ParameterKey':'DBSecurity','ParameterValue':dbsecurity},\
					{'ParameterKey':'DBName','ParameterValue':dbname},\
					{'ParameterKey':'DBUserName','ParameterValue':dbusername},\
					{'ParameterKey':'DBPassword','ParameterValue':dbpassword},\
					{'ParameterKey':'DeletionProtection','ParameterValue':deletionprotection}\
					])
rds_waiter = client.get_waiter('stack_create_complete')
try:
	rds_waiter.wait(StackName = response_rds['StackId'])
except:
	print('RDS Stack creation failed. Exiting the script')
	exit(1)
rds = client.describe_stack_resources(StackName=rds_stackname)
print('RDS stack created successfully')
#print(rds)
print('All stacks successfully completed')
