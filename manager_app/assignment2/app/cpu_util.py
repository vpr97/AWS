from app import managerapp
from app import config
import boto3
import sys
from app import asp
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
from flask import Flask


#-------------------------------
# redis_app = Flask(__name__)

# r = redis.Redis()
# q = Queue(connection=redis)

#-------------------------------------

elbList = boto3.client(
    service_name='elbv2'
    )
ec2 = boto3.client(
    service_name='ec2'
    )


def instancename(instanceid):
    instances=ec2.describe_instances(Filters=[
        {
            'Name': 'instance-id',
            'Values': [
                instanceid
            ]
        },
    ],)
    for instance in instances["Reservations"]:
        for inst in instance["Instances"]:
            for tag in inst["Tags"]:
                if tag['Key'] == 'Name':
                    return (tag['Value'])
    print(tag['Value'])

# def correct_list(cpu_util_total, running_instances):
#     if len(cpu_util_total) == len(running_instances):
#         min_len = min(map(len,cpu_util_total))
#         print(min_len)
#         list_to_return = []
#         for item in cpu_util_total:
#             if(len(item)>min_len):
#                 last = -1
#                 start = (len(item) - min_len) - 1 
#                 list_to_return.append(item[start:last])
#             else:
#                 list_to_return.append(item[0:])
#         return list_to_return
            
            
        
            

def cpu_utilization():
    running_instances = []
    ALB_list = elbList.describe_target_health(TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:907616474711:targetgroup/LoadBalancerTG/6849c52527f78fbc')
    for elb in ALB_list['TargetHealthDescriptions']:
        # elb['Name'] = instancename(elb['Target']['Id'])
        if (elb['TargetHealth']['State']) == 'healthy':
            running_instances.append(elb['Target']['Id'])
    #print(running_instances) #all healthy instances are appended in this list
        
    
    # cpu_timestamp = []
    cpu_util_total = []
    client = boto3.client('cloudwatch')
    for item in running_instances:
        response = client.get_metric_statistics(
            
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
             Dimensions=[
                        {
                'Name': 'InstanceId',
                'Value': item
                        },
                    ],
                    StartTime=datetime.utcnow() - timedelta(seconds=5 * 60),
                    EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
                    Period=1*60,
                    Statistics=[
                        'Average'
                    ],
                    Unit='Percent'
                )
        # print(response)
        #print(sorted(response, key=response.get))
        cpu_timestamp=[]
        cpu_util = []
        for cpu in response['Datapoints']:
            
            #if 'Average' in cpu:
            #print(cpu)
            #cpu_util.append(cpu['Average'])
            cpu_timestamp.append(cpu)
        #cpu_util_total.append(cpu_util)
        newlist = sorted(cpu_timestamp, key = itemgetter('Timestamp'))
        #print("newlist--->",newlist)
        
        for element in newlist:
            cpu_util.append(element['Average'])
        #cpu_util = (newlist, key = itemgetter('Average'))
        #print("sorted_cpu_util------",cpu_util)
        #print(len(cpu_util))
        cpu_util_total.append(cpu_util)
    #print("cpu_util_total------",cpu_util_total)
    # cpu_util_list = correct_list(cpu_util_total,running_instances)
    # print("cpu_util_list_after_adjustment------",cpu_util_list)
    print("cpu_util_total-------->", cpu_util_total)
    asp.auto_scaling_policy(running_instances,cpu_util_total)


# def avg_util_calc ():
# i = 0
# j = 0
# avg_util_1 = 0
# for i in range(len(running_instances)):
#     avg_util_1 += CPU_util_total [i][j]
#     i = i + 1
# avg_util_total_1 = avg_util_1 / (len(running_instances))

# avg_util_2 = 0
# k = 0
# l = 1
# for k in range(len(running_instances)):
#     avg_util_2 += CPU_util_total [k][l]
#     k = k + 1
# avg_util_total_2 = avg_util_2 / (len(running_instances))


# if ((avg_util_total_1*2)<=avg_util_total_2):
#     print("Increase instance count")
# elif ((avg_util_total_1*2)>avg_util_total_2):
#     if (avg_util_total_1>(avg_util_total_2*2)):
#         print("Decrease instance count")
#     else:
#         print("No change")
        
        

# avg_util = 0
# for data in CPU_util:
#     avg_util+=data
# avg_util_total = avg_util / (len(CPU_util))

# if avg_util_total > 10:
#     print ("Exceeded Threshold")
# else:
#     print("No Problem")


# @redis_app.route("/")
# def start_redis():
#     job = q.enqueue(cpu_utilization)
    
    
# if __name__ == "__main__":
#     redis_app.run()


    


    
    