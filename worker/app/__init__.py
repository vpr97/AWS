from flask import Flask
webapp = Flask(__name__)

from app import login
from app import register
from app import upload_auth
from app import forgot_password
from app import api
#from app import count
from app import delete_user
