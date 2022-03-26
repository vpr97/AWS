from app import managerapp
from app import config
import math
import boto3
import sys
import time
import datetime, timedelta
from app import cpu_util 
from app import create_delete  


# def modify_instance_count(ratio,n):
#     if(ratio>=2 and n<=3):
#         count = n;
#         while(count>0):
#             #function to start a instance (We can include sleep function in start and remove instance)
#             print("Creating new Instance")
#             create_delete.create_new_instance()
#             count = count - 1
#         i=0
#         for i in range (0,300):
#             time.sleep(1)
#             i=i+1
#         cpu_util.cpu_utilization()
#     if(ratio>=2 and n>3):
#         if n>=6:
#             pass
#         else:
#             print("Creating new Instance n>3")
#             create_delete.create_new_instance()
#             create_delete.create_new_instance()
#             i=0
#             for i in range (0,300):
#                 time.sleep(1)
#                 i=i+1
#             cpu_util.cpu_utilization()
#     if(ratio<=0.5 and n>3):
#         count = math.floor(n/2)
#         while(count>0):
#             create_delete.delete_instances()
#             count = count -1
#         i=0
#         for i in range (0,300):
#             time.sleep(1)
#             i=i+1
#         cpu_util.cpu_utilization()
#     if(ratio<=0.5 and n<3):
#         count = math.floor(n/2)
#         while(count>0):
#             print("Removing Instance")
#             create_delete.delete_instances()
#             count = count - 1
#         i=0
#         for i in range (0,300):
#             time.sleep(1)
#             i=i+1
#         cpu_util.cpu_utilization()
#     if(ratio>0.5 and ratio<2):
#         print("Ratio inside ASP------->",ratio)
#         print("No change in state.")
#         i=0
#         for i in range (0,120):
#             time.sleep(1)
#             i=i+1
#         #wait for few mins and call CPU utilization
#         cpu_util.cpu_utilization()
#         #call CPU utilization function   

def modify_instance_count(average_utilization,n):
    print("Into modify_instance_count Function")
    expand_ratio = 2
    shrink_ratio = 0.25
    expand_threshold = 3
    shrink_threshold = 0.2


    if average_utilization>=20 and average_utilization<=90:
        print("Into expand Threshold")
        if average_utilization>=expand_threshold:
            if(n<6):
                if expand_ratio == 2:
                    if n<=3:
                        i=0
                        print("n---->",n)
                        for i in range(0,n):
                        # for(i=0;i<n;i++):
                            i=i+1
                            create_delete.create_new_instance()
                    elif n>3:
                        i=0
                        for i in range(n,6-n):
                        # for(i=n;i<6-n<;i++):
                            i=i+1
                            create_delete.create_new_instance()
                elif expand_ratio == 3:
                    if n<=2:
                        i=0
                        for i in range(0,2*n):
                        # for(i=0;i<2n;i++):
                            i = i+1
                            create_delete.create_new_instance()
                    elif n>2:
                        i=0
                        for i in range(n,6):
                        # for(i=n;i<6;i++):
                            i=i+1
                            create_delete.create_new_instance() 
                elif expand_ratio == 4:
                    if n==1:
                        i=0
                        for i in range(0,3):
                        # for(i=0;i<3;i++):
                            i=i+1
                            create_delete.create_new_instance()
                    elif n>1:
                        i=n
                        while(n<6):
                           create_delete.create_new_instance()
                           i=i+1
                i=0
                for i in range (0,120):
                    time.sleep(1)
                    i=i+1
                cpu_util.cpu_utilization()
            else:
                i=0
                for i in range (0,60):
                    time.sleep(1)
                    i=i+1
                cpu_util.cpu_utilization()
        else:
            i=0
            for i in range (0,60):
                time.sleep(1)
                i=i+1
            cpu_util.cpu_utilization()
                
    elif average_utilization>=0.5 and average_utilization<15:
        print("Into Shrink Threshold")
        if average_utilization<=shrink_threshold:
            if(n!=1):
                if shrink_ratio == 0.5:
                    a = math.floor(n-(n/(100/50)))
                    for i in range(0,a):
                        i=i+1
                        create_delete.delete_instances()
                if shrink_ratio == 0.25:
                    a = math.floor(n-(n/(100/25)))
                    for i in range(0,a):
                        i=i+1
                        create_delete.delete_instances()
                if shrink_ratio == 0.75:
                    a = math.floor(n-(n/(100/75)))
                    for i in range(0,a):
                        i=i+1
                        create_delete.delete_instances()
            i=0
            for i in range (0,120):
                time.sleep(1)
                i=i+1
            cpu_util.cpu_utilization()
        else:
            print("No Change in shrinking")
            i=0
            for i in range (0,60):
                time.sleep(1)
                i=i+1
                #print("i------->",i)
            cpu_util.cpu_utilization()
    else:
        print("No Change")
        i=0
        for i in range (0,60):
            time.sleep(1)
            i=i+1
        cpu_util.cpu_utilization()
    
    

# def calculate_ratio(first,second):
#     # first = int(first)
#     # second = int(second)
#     print ("Into calculating ratio")
#     print(first)
#     print(second)
#     return second/first


def auto_scaling_policy(running_instances,cpu_util_list):
    
    n = len(running_instances) 
    print("running_instances---->",n)
    average_utilization = 0
    if n==1:
        # ratio = cpu_util_list[0][1] / cpu_util_list[0][0]
        average_utilization = cpu_util_list[0][0]
        print("Only one instance")
    else:
        sum_utilization = 0
        i = 0
        for i in range(n):
            sum_utilization = cpu_util_list[i][0]
            i = i+1
        average_utilization = sum_utilization/n
        
    modify_instance_count(average_utilization,n)
    
        # i=0
        # j=0
        # utilization_all_instances_first = 0
        # utilization_all_instances_second = 0
        
        
        # for i in range(n):
        #     print(cpu_util_list[i][j])
        #     utilization_all_instances_first = utilization_all_instances_first+ cpu_util_list[i][j]
        #     i = i+1
        # average_utilization_first = utilization_all_instances_first/n
        
        # k=0
        # l=1
        # for k in range(n):
        #     utilization_all_instances_second = utilization_all_instances_second+ cpu_util_list[k][l]
        #     k=k+1
        # average_utilization_second = utilization_all_instances_second/n
        
        # ratio = calculate_ratio(average_utilization_first,average_utilization_second)
        # print("ratio------->",ratio)
        
  
    
                            
                    
                
            
        

    
    