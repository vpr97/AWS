#from threading import Thread
from app import cpu_util
import sys
import multiprocessing
import boto3
from app import manager_home
import time
import os
#import psutil
# import atexit
# from apscheduler.schedulers.background import BackgroundScheduler
# scheduler = BackgroundScheduler()

elbList =  boto3.client('elbv2')

#!venv/bin/python 
from app import managerapp
#webapp.run(host='0.0.0.0',debug=True)


# thread = Thread(target = cpu_util.cpu_utilization)
# thread.start()
all_instances = []
ALB_list = elbList.describe_target_health(TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc')
for elb in ALB_list['TargetHealthDescriptions']:
    #elb['Name'] = instancename(elb['Target']['Id'])
    if (elb['TargetHealth']['State']) == 'healthy':
        all_instances.append(elb['Target']['Id'])
if len(all_instances) == 0:
    print("No instances on startup")
    # error_msg = "Please wait while a new worker instance is starting"
    manager_home.create_new_instance()
    i =0
    for i in range(0,60):
        time.sleep(1)
        i = i + 1
    # error_msg = "New workder instance created on startup"
else:
    pass

managerapp.run(host='0.0.0.0', port=5000,debug = False) 

thread = multiprocessing.Process(target = cpu_util.cpu_utilization)
thread.start()
thread.terminate()

   

# # print("1------->",thread,thread.is_alive())

# # print("2------->",thread,thread.is_alive())
# # pid = thread.pid
# # print("Pid---------->",pid)

# # p = psutil.Process(pid)
# # thread.terminate()  #or p.kill()
# # time.sleep(0.1)
# # print("3------->",thread,thread.is_alive())
