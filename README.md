** AWS Project 1 **



** Create a new VPC, RDS, Elastic Beanstalk environment and an S3 bucket **
* VPC gives an option to create public or private&public subnets
* Elastic Beanstalk gives an option to create a JAVA, PHP, Python or Node.js environment
* The cfn files don't require any inputs, unless the hardcoded values have to be changed
* All hardcoded values are in cfn-ebs.yaml
* All user inputs are in create.py files
* There is no script to delete or modify. Those will have to be run from the console
* ** To run the script - ./create.py **


** Manual Steps **
* Create a new SSH key
* Create a new SSL Certificate
* Domain should already be setup in Route53


** HardCoded Values **
* AWS Location of where the sample configuration files are to be downloaded from
* Current Solution Stack Ids - Can get the most current by running aws elasticbeanstalk list-available-solution-stacks and parsing for the most recent environment
* Route53HostedZoneID - Values at https://docs.aws.amazon.com/general/latest/gr/rande.html#elb_region

** To fully automate, the above 6 issues have to be addressed **
