from flask import render_template, redirect, url_for, request
from app import managerapp

import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter




@managerapp.route('/instance_details/<id>',methods=['GET'])

def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')


    namespace = 'AWS/EC2'
    statistic = 'Average'                   



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='CPUUtilization',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))

    namespace = 'AWS/Logs'
    

    http_rate = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='IncomingLogEvents',
        Namespace=namespace,  
        Statistics=[statistic],
        Dimensions=[{'Name': 'LogGroupName', 'Value': id}]
    )

    http_rate_stats = []
    print(http_rate_stats)

    for point in http_rate['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        http_rate_stats.append([time,point['Average']])

    http_rate_stats = sorted(http_rate_stats, key=itemgetter(0))
    return render_template("view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           http_rate_stats=http_rate_stats)

                  



 