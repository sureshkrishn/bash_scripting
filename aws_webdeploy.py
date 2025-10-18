import boto3

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)
ec2_resource = boto3.resource('ec2', region_name=region)

key_pair_name = 'aws-n.virginia-kp1'
security_group_name = 'webserver-sec-group'
description = 'Security group for testserver01 allowing HTTP, HTTPS, and SSH'

# Latest free tier eligible Ubuntu 22.04 LTS AMI for us-east-1 (verify periodically)
ubuntu_ami = 'ami-04505e74c0741db8d'

# Check if security group exists
response = ec2.describe_security_groups(
    Filters=[{'Name': 'group-name', 'Values': [security_group_name]}]
)

if len(response['SecurityGroups']) > 0:
    security_group_id = response['SecurityGroups'][0]['GroupId']
    print(f"Using existing security group '{security_group_name}' with id: {security_group_id}")
else:
    # Create security group
    vpc_id = list(ec2.describe_vpcs()['Vpcs'])[0]['VpcId']
    response = ec2.create_security_group(
        GroupName=security_group_name,
        Description=description,
        VpcId=vpc_id
    )
    security_group_id = response['GroupId']
    print(f"Created new security group '{security_group_name}' with id: {security_group_id}")

    # Add ingress rules for SSH, HTTP, HTTPS
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        ]
    )
    print("Ingress rules set for SSH, HTTP, and HTTPS.")

user_data_script = """#!/bin/bash
apt update -y
apt install -y apache2 wget unzip
cd /tmp
wget https://www.tooplate.com/zip-templates/2108_dashboard.zip
unzip 2108_dashboard.zip
chmod -R 777 /tmp /var/www /var/www/html
mv /tmp/2108_dashboard/* /var/www/html/
systemctl restart apache2
systemctl enable apache2
"""

instance = ec2_resource.create_instances(
    ImageId=ubuntu_ami,
    InstanceType='t3.micro',
    KeyName=key_pair_name,
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[security_group_id],
    UserData=user_data_script,
    TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'testserver01'}]}]
)

print(f"Launching EC2 instance 'testserver01' with ID: {instance[0].id}")
instance[0].wait_until_running()
instance[0].reload()
print(f"Instance Public IP: {instance[0].public_ip_address}")
print("Website should be accessible at the above IP once Apache setup completes.")
