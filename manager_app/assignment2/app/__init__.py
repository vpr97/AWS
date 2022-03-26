from flask import Flask
managerapp = Flask(__name__)

from app import manager_home
from app import instance_details
from app import config
from app import create_delete
from app import asp
from app import cpu_util
from app import tune_autoscaler