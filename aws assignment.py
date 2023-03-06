import boto3
from datetime import datetime

aws_management_console= boto3.session.Session(profile_name="default")
aws_ec2_access=aws_management_console.client(service_name='ec2')

aws_asg=aws_management_console.client(service_name='autoscaling')

asg_name = 'lv-test-cpu'

response1 = aws_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
desired_capacity = response1['AutoScalingGroups'][0]['DesiredCapacity']
print(f"Desired capacity of ASG '{asg_name}': {desired_capacity}")

ec2_response = aws_ec2_access.describe_instances()
num_instances = len(ec2_response['Reservations'])

# Testcase1: Verify number of running instances matches the desired capacity
if num_instances != desired_capacity:
    print("ERROR: Number of running instances does not match the desired capacity of the ASG!")
else:
    print("Number of running instances matches the desired capacity of the ASG.")

# Testcase 2: verify that if more than 1 instances already running on ASG, then ec2 instance should on availble on multiple availibity zone

response = aws_asg.describe_auto_scaling_groups(
    AutoScalingGroupNames=[asg_name],
    MaxRecords=1
)
instances = response['AutoScalingGroups'][0]['Instances']

if len(instances) > 1:

    availzone_set = set()
    for instance in instances:
        response = aws_ec2_access.describe_instances(
            InstanceIds=[instance['InstanceId']]
        )
        availzone_set.add(response['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone'])

    if len(availzone_set) == 1:
        print('The instances are not launched in multiple Availability Zones')
    else:
        print('The instances are launched in multiple Availability Zones')

#Testcase:3 Verify SecuirtyGroup, ImageID and VPCID should be same on ASG running instances.

# Instance ID: i-0255b3aef45bc3535
# Instance ID: i-0cd86ce526b38d65c
asg_name = 'lv-test-cpu'
instance_info1 = aws_ec2_access.describe_instances(InstanceIds=['i-0255b3aef45bc3535'])
for reservation in instance_info1['Reservations']:
    for first_instance in reservation['Instances']:
        first_sg_id = first_instance['SecurityGroups'][0]['GroupId']
        first_image_id = first_instance['ImageId']
        first_vpc_id = first_instance['VpcId']

instance_info = aws_ec2_access.describe_instances(InstanceIds=['i-0cd86ce526b38d65c'])

for reservation in instance_info['Reservations']:
    for instance in reservation['Instances']:
        sg_id = instance['SecurityGroups'][0]['GroupId']
        image_id = instance['ImageId']
        vpc_id = instance['VpcId']
if sg_id != first_sg_id or image_id != first_image_id or vpc_id != first_vpc_id:
    print("Instances has different Security Group ID, Image ID, or VPC ID than the first instance.")
else:
    print("SecuirtyGroup, ImageID and VPCID should be same on ASG running instances")


# Testcase:4 Findout uptime of ASG running instances
asg_instances = aws_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])['AutoScalingGroups'][0]['Instances']
instance_ids = [instance['InstanceId'] for instance in asg_instances]

# get instance launch time
instances_info = aws_ec2_access.describe_instances(InstanceIds=instance_ids)
for reservation in instances_info['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        launch_time = instance['LaunchTime']
        current_time = datetime.now(launch_time.tzinfo)
        uptime = current_time - launch_time
        print(f"Instance {instance_id} has been running for {uptime}.")

