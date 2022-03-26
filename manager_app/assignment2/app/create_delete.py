from app import managerapp
from app import config
#from load_balancing import webapp
import boto3
import sys
import time



ec2_client = boto3.client('ec2')
elbList =  boto3.client('elbv2')

def create_new_instance():
    print("Inside the create function!")
    instance_id = ''
    user_data = '''#!/bin/bash
                   sudo apt-get install apache2 -y
                   sudo systemctl start apache2.service
                   sudo chmod 0777 /var/log/apache2/access.log
                   sudo chmod 0777 /var/log/apache2/error.log
                   sudo -u ubuntu -H sh -c "python3 /home/ubuntu/run.py"
                   sudo -u ubuntu -H sh - c "gunicorn --bind 0.0.0.0:5000 --error-logfile /var/log/apache2/error.log --access-logfile /var/log/apache2/access.log --capture-output --log-level debug app:webapp"'''
    
    instances = ec2_client.run_instances(
             BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': True,
                    # 'Iops': 100,
                    'VolumeSize': 8,
                    'VolumeType': 'gp2',
                    'Encrypted': False
                },
            },
        ],
            ImageId="ami-0ce106d8d355743bc",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.medium",
            KeyName="ece1779",
            Monitoring={'Enabled': True},
            Placement={
            'AvailabilityZone': 'us-east-1b',
        },
            # SecurityGroupIds=[
            # 'sg-0f532c2818b5f5b86',
            # ],
            # SecurityGroups=[
            #     'launch-wizard-10',
            # ],
            # SubnetId='subnet-1e017a53',
            UserData=user_data,
            IamInstanceProfile={
                'Arn': 'arn:aws:iam::907616474711:instance-profile/assignment2_role'
                #'Name': 'assignment2_role'
            },
         NetworkInterfaces=[
        {
            'AssociatePublicIpAddress': True,
            'DeleteOnTermination': True,
            'Description': 'Primary Interface',
            'DeviceIndex': 0,
            'Groups': [
                'sg-0f532c2818b5f5b86',
            ],
            'SubnetId': 'subnet-1e017a53',
        },
    ]
    )
    print(instances["Instances"][0]["InstanceId"])
    i=0
    for i in range (0,120):
        time.sleep(1)
        i=i+1
    print("Instance in running state")
    instance_id = instances["Instances"][0]["InstanceId"]
    
    print("Adding into the target group!")
    response = elbList.register_targets(
    TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc',
    Targets=[
        {
            'Id': instance_id,
            'Port': 5000
            #'AvailabilityZone': 'us-east-1b'
        },
    ]
    )
    
    
        
# def instancename(instanceid):
#     instances=ec2_client.describe_instances(Filters=[
#         {
#             'Name': 'instance-id',
#             'Values': [
#                 instanceid
#             ]
#         },
#     ],)
#     for instance in instances["Reservations"]:
#         for inst in instance["Instances"]:
#             for tag in inst["InstanceId"]:
#                 return (tag)

def delete_instances():
    all_instances = []
    ALB_list = elbList.describe_target_health(TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc')
    for elb in ALB_list['TargetHealthDescriptions']:
        #elb['Name'] = instancename(elb['Target']['Id'])
        if (elb['TargetHealth']['State']) == 'healthy':
            all_instances.append(elb['Target']['Id'])
    print(all_instances)
    
    instance_to_be_deleted = all_instances[-1]
    print(instance_to_be_deleted)
    ec2_client.terminate_instances(
        
        InstanceIds=[
        instance_to_be_deleted,
        ],
        DryRun=False
        )
    time.sleep(30)
            
    
    