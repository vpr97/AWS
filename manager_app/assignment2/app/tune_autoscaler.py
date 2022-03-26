from app import managerapp
from app import config
from flask import request, render_template,redirect, url_for
from threading import Thread
import multiprocessing

@managerapp.route('/tune_autoscaling')
def tune_autoscaling():
    
    return render_template('alter_autoscaling.html')

    
# @managerapp.route('/stp_asp')
# def stop_asp():
    
#     thread = multiprocessing.Process(target = cpu_util.cpu_utilization)
#     print("1------->",thread.is_alive())
#     thread.start()
#     print("2------->",thread.is_alive())
#     pid = thread.pid
#     print("Pid---------->",pid)
#     # thread.terminate()
#     p = psutil.Process(pid)
#     thread.terminate()  #or p.kill()

    
#     return render_template('alter_autoscaling.html')