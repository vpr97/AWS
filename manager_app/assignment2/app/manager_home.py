from flask import request, render_template,redirect, url_for
from app import managerapp
import mysql.connector
import boto3
import time
from app import config
from datetime import datetime, timedelta
from operator import itemgetter
from app import cpu_util
import mysql.connector


s3 = boto3.client(
    service_name='s3'
)

ec2_client = boto3.client('ec2')
elbList =  boto3.client('elbv2')

def create_new_instance():
    print("Inside the function!")
    instance_ids = []
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
    instance_ids.append(instances["Instances"][0]["InstanceId"])
    print("instance_ids----", instance_ids)
    
    for item in instance_ids:
        print("Adding into the target group!")
        response = elbList.register_targets(
        TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc',
        Targets=[
            {
                'Id': item,
                'Port': 5000
                #'AvailabilityZone': 'us-east-1b'
            },
        ]
        )
        
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

@managerapp.route('/', methods=['GET', 'POST'])
def login():
    # cpu_util.cpu_utilization()
    return render_template('login_page.html')
    
@managerapp.route('/home',methods=['GET', 'POST'])
def manager_login():
    n1 = request.form.get('username')
    n2 = request.form.get('password')

    if n1 == '' or n2 == '':
        error_msg = "Username or Password should not be blank!"
        return render_template('login_page.html', error_msg=error_msg)
    if n1 =='manager' and n2=='manager':
        return render_template('manager_home.html')
    else:
        error_msg = "Username or Password incorrect!"
        return render_template('login_page.html', error_msg=error_msg)
    

@managerapp.route('/manager_home')
def go_to_manager_page():
    
    
    client = boto3.client('cloudwatch')
    statistic = 'Average'                   

    namespace = 'AWS/ApplicationELB';

    worker = client.get_metric_statistics(
   
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='HealthyHostCount',
        Namespace=namespace,  
        Statistics=[statistic],
        Dimensions=[{'Name': 'TargetGroup', 'Value': 'targetgroup/LoadBalancerTG/6849c52527f78fbc'},{'Name': 'LoadBalancer', 'Value': 'app/assignment/022dc9adcec95ce2'}]
    )

    worker_stats = []


    for point in worker['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        worker_stats.append([time,point['Average']])

    worker_stats = sorted(worker_stats, key=itemgetter(0))
    return render_template('manager_home.html',
                            worker_stats=worker_stats)
    

@managerapp.route('/delete_all_S3', methods=['GET', 'POST'])

def delete_s3():
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket('assignment2ece1779')
    bucket.objects.all().delete()
    delete_message = "All Contents of S3 Buckets is deleted."
    return render_template('manager_home.html', delete_message=delete_message)

@managerapp.route('/delete_all_rds', methods=['GET', 'POST'])

def delete_rds():

    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("TRUNCATE TABLE image_path;")
    cred.commit()
    cursor.execute("DELETE FROM user_accounts where user!='admin';")
    cred.commit()
    
    delete_message = "All data from RDS Database is deleted."
    return render_template('manager_home.html', delete_message=delete_message)
    
    cursor.close()
    cred.close()
    
@managerapp.route('/ec2_instances_list', methods=['GET', 'POST'])

def display_worker_instances_list():
    
    # status = request.form.get('filter', "")
    
    ec2 = boto3.resource('ec2')
    
    elbList =  boto3.client('elbv2')
    all_instances = []
    ALB_list = elbList.describe_target_health(TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc')
    for elb in ALB_list['TargetHealthDescriptions']:
        #elb['Name'] = instancename(elb['Target']['Id'])
        if (elb['TargetHealth']['State']) == 'healthy':
            all_instances.append(elb['Target']['Id'])
    

    instances =ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running'] 
                },
                
                {
                    'Name' :'instance-id',
                    'Values' : all_instances
                }
                
            ]
        )
   
    return render_template("all_ec2_instances_details.html",instances=instances)

@managerapp.route('/destroy_ec2_instance/<id>', methods=['GET', 'POST'])
def ec2_destroy(id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[id]).terminate()
    
    
    
    return redirect(url_for('display_worker_instances_list'))
    
    
@managerapp.route('/start_ec2_instance', methods=['GET', 'POST'])
def start_ec2():
    print("Into Create Instance")
    create_new_instance()
    error_msg = "Instance is created."
    return render_template("manager_home.html",error_msg=error_msg)
    
@managerapp.route('/terminate_ec2_instance', methods=['GET', 'POST'])
def terminate_ec2():
    print("Into Terminate Instance")
    delete_instances()
    error_msg = "Instance is terminated."
    return render_template("manager_home.html",error_msg=error_msg)

@managerapp.route('/stop_ec2_instance', methods=['GET', 'POST'])    
def stop_ec2():
    
    ec2 = boto3.resource('ec2')

    
@managerapp.route('/stop_manager_app', methods=['GET', 'POST'])
def stop_manager():
    
    ec2 = boto3.resource('ec2')
    
    ids = ['i-01050eb482eb55f9d']
    
    ec2.instances.filter(InstanceIds = ids).stop()
    elbList =  boto3.client('elbv2')
    all_instances = []
    ALB_list = elbList.describe_target_health(TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc')
    for elb in ALB_list['TargetHealthDescriptions']:
        #elb['Name'] = instancename(elb['Target']['Id'])
        if (elb['TargetHealth']['State']) == 'healthy':
            all_instances.append(elb['Target']['Id'])
    
    ec2.instances.filter(InstanceIds = all_instances).terminate()
    error_msg = "Manager App is stopped."
    return render_template("manager_home.html",error_msg=error_msg)
    
    
    