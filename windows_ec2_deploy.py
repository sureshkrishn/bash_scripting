import boto3
import time

# Initialize boto3 EC2 client
ec2_client = boto3.client('ec2', region_name='us-east-1')

# Key Pair name
key_name = "N.virgina_windows"  # Replace with your key pair name

# AMI ID for Windows Server 2019 Free Tier (Update with appropriate free-tier AMI)
windows_ami_id = "ami-0e3c2921641a4a215"  # Example AMI for Windows 2019

# Instance Type (t2.micro is Free Tier eligible)
instance_type = 't3.micro'

# Security group settings for RDP (port 3389)
security_group_name = "my-windows-security-group"
security_group_description = "Security group for RDP access to Windows EC2 instance"

# Create a security group for RDP (Port 3389)
def create_security_group():
    response = ec2_client.create_security_group(
        GroupName=security_group_name,
        Description=security_group_description
    )
    security_group_id = response['GroupId']
    
    # Add an inbound rule for RDP (TCP port 3389)
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 3389,
                'ToPort': 3389,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Open to all IPs (you can restrict it for security)
            }
        ]
    )
    return security_group_id

# Launch the EC2 instance
def launch_ec2_instance(security_group_id):
    response = ec2_client.run_instances(
        ImageId=windows_ami_id,  # Windows AMI
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],  # Use the created security group
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': 'Windows-Free-Tier-Instance'}
                ]
            }
        ]
    )
    
    instance_id = response['Instances'][0]['InstanceId']
    print(f"EC2 Instance created: {instance_id}")

    return instance_id

# Wait until the instance is running and get public IP
def get_instance_public_ip(instance_id):
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    # Fetch instance details to get public IP
    instance_details = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_details['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f"Instance public IP: {public_ip}")

    return public_ip

# Main function
def main():
    # Step 1: Create security group
    security_group_id = create_security_group()

    # Step 2: Launch EC2 instance
    instance_id = launch_ec2_instance(security_group_id)

    # Step 3: Wait for instance to be running and fetch public IP
    public_ip = get_instance_public_ip(instance_id)

    print(f"Access your Windows EC2 instance at: {public_ip} via RDP")

if __name__ == "__main__":
    main()
