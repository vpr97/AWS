import mysql.connector
from flask import jsonify
from app import webapp
import os
from flask import request, render_template
from werkzeug.utils import secure_filename
from PIL import Image as Image1
from wand.image import Image
from passlib.hash import sha256_crypt
from app.upload_auth import file_format
import random
import string
import urllib.request
import boto3

UPLOAD_FOLDER = '/home/ubuntu/assignment2/app/static/uploads'
webapp.secret_key = "secret key"
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webapp.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
user_transform_images = []
path_extract_tuple = []
path_extract = []
all_uploaded_images = []

s3 = boto3.client(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id='Access key',
    aws_secret_access_key='secret key'
)

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# def allowed_fileapi(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


user_dict = {}

#function to test register functionality using postman
@webapp.route('/api/register', methods=['POST','GET'])
def registerapi():
    
    
    
    new_user = request.form.get('username')
    new_password = request.form.get('password')
    new_enc_password = sha256_crypt.encrypt(new_password)
    new_is_admin = False
    new_mail = "testapi@gmail.com"
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")
    if new_user == '' or new_password == '':
        return jsonify(
            {
                "success": "false",
                "error": {
                    "code": 200,
                    "message": "Enter Username and Password!"
                }
            }
        )
    else:
        for (user, password, email, is_admin) in cursor:
            user_dict[user] = password

        if new_user in user_dict.keys():
            return jsonify(
                {
                    "success": "false",
                    "error": {
                        "code": 200,
                        "message": "User already exists!"
                    }
                }
            )
        else:
            add_user = ("INSERT INTO user_accounts VALUES (%s, %s, %s, %s);")
            cursor.execute(add_user, (new_user, new_enc_password, new_mail, new_is_admin,))
            cred.commit()
            bucket_name = "assignment2ece1779"
            directory_name = new_user
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/'))
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/thumb/'))
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/transform/'))
            return jsonify(
                {
                    "success": "true",
                }
            )

    cursor.close()
    cred.close()

# ----------------------------------------------------------------------------------------------------------

#function to test upload functionality using postman
@webapp.route('/api/upload', methods=['GET', 'POST'])
def uploadapi():
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")

    for (user, password, email, is_admin) in cursor:
        user_dict[user] = password

    cursor.close()
    cred.close()
    

    n1 = request.form.get('username')
    n2 = request.form.get('password')
    
    
    # multiple files of same name
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor(buffered=True)
    query = ("SELECT path from image_path where user = %s;")
    cursor.execute(query, (str(n1),))
    for row in cursor:
        path_extract_tuple.append(row)

    cursor.close()
    cred.close()
    for path in path_extract_tuple:
        path_extract.append(''.join(path))

    for fullpath in path_extract:
        fullpath_list = (fullpath.split('/'))[-1]
        all_uploaded_images.append(fullpath_list)

    if n1 == "" or n2 == "":
        return jsonify(
            {
                "success": "false",
                "error": {
                    "code": 200,
                    "message": 'Username or Password cannot be empty!'
                }
            })

    if n1 in user_dict.keys():
        if sha256_crypt.verify(n2, user_dict[n1]):
            if request.method == "POST":
                image = request.files['file']
                if image.filename == '':
                    return jsonify(
                        {
                            "success": "false",
                            "error": {
                                "code": 200,
                                "message": 'No image selected for uploading!'
                            }
                        })
                if image:
                    filename = secure_filename(image.filename)
                    if filename in all_uploaded_images:
                        letters = string.ascii_lowercase
                        random_name = (''.join(random.choice(letters) for i in range(6)))
                        filename = filename.split('.')[0]
                        image_format = file_format(image.filename)
                        filename = filename + '_' + random_name + image_format
                        image.save(os.path.join(webapp.config['UPLOAD_FOLDER'], filename))
                        imagepath = UPLOAD_FOLDER + '/' + filename
                        user_session = n1
                    
                    else:
                        
                        image.save(os.path.join(webapp.config['UPLOAD_FOLDER'], image.filename))
                        user_session = n1
                        s3_storage_path = user_session+"/transform/"+image.filename
                        imagepath = UPLOAD_FOLDER + '/' + image.filename
                        s3.upload_file(imagepath,'assignment2ece1779',s3_storage_path)

                    
                    format = file_format(image.filename)
                    thumb_name_list = filename.split(".")
                    thumb_extract = thumb_name_list[0]
                    THUMB_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_thumb' + format
                    thumb_list = THUMB_FOLDER.split("/")
                    thumb_name = thumb_list[-1]

                    THUMB_s3 = user_session + '/thumb/' + thumb_extract + '_thumb' + format
                    thumb = Image1.open(imagepath)
                    MAX_SIZE = (100, 100)
                    thumb.thumbnail(MAX_SIZE)
                    thumb.save(THUMB_FOLDER)
                    s3.upload_file(THUMB_FOLDER,'assignment2ece1779',THUMB_s3)
                    
                    BLUR_s3 = user_session + '/transform/' + thumb_extract + '_blur' + format
                    blur_image = Image(filename=imagepath)
                    BLUR_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_blur' + format
                    blur_list = BLUR_FOLDER.split("/")
                    blur_name = blur_list[-1]
                    blur_image.blur(radius=0, sigma=8)
                    blur_image.save(filename=BLUR_FOLDER)
                    s3.upload_file(BLUR_FOLDER,'assignment2ece1779',BLUR_s3)

                    SHADE_s3 = user_session + '/transform/' + thumb_extract + '_shade' + format
                    shade_image = Image(filename=imagepath)
                    SHADE_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_shade' + format
                    shade_list = SHADE_FOLDER.split("/")
                    shade_name = shade_list[-1]
                    shade_image.shade(gray=True, azimuth=286.0, elevation=45.0)
                    shade_image.save(filename=SHADE_FOLDER)
                    s3.upload_file(SHADE_FOLDER,'assignment2ece1779',SHADE_s3)

                    SPREAD_s3 = user_session + '/transform/' + thumb_extract + '_spread' + format
                    spread_image = Image(filename=imagepath)
                    SPREAD_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_spread' + format
                    spread_list = SPREAD_FOLDER.split("/")
                    spread_name = spread_list[-1]
                    spread_image.spread(radius=8)
                    spread_image.save(filename=SPREAD_FOLDER)
                    s3.upload_file(SPREAD_FOLDER,'assignment2ece1779',SPREAD_s3)

                    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
                    cursor = cred.cursor()
                    query = ("INSERT INTO image_path VALUES(%s,%s);")
                    cursor.execute(query, (n1, imagepath,))
                    cred.commit()
                    cursor.close()
                    cred.close()

                    original_size = os.stat(os.path.join(webapp.config['UPLOAD_FOLDER'], image.filename)).st_size
                    blur_size = os.stat(
                        os.path.join(webapp.config['UPLOAD_FOLDER'], thumb_extract + '_blur' + format)).st_size
                    shade_size = os.stat(
                        os.path.join(webapp.config['UPLOAD_FOLDER'], thumb_extract + '_shade' + format)).st_size
                    spread_size = os.stat(
                        os.path.join(webapp.config['UPLOAD_FOLDER'], thumb_extract + '_spread' + format)).st_size
                    return jsonify(
                        {
                            "success": "true",
                            "payload": {
                                "original_size": original_size,
                                "blur_size": blur_size,
                                "shade_size": shade_size,
                                "spread_size": spread_size

                            }
                        }
                    )
        else:
            return jsonify(
                {
                    "success": "false",
                    "error": {
                        "code": 200,
                        "message": "Invalid Password."
                    }
                })
    else:
        return jsonify(
            {
                "success": "false",
                "error": {
                    "code": 200,
                    "message": "Invalid User."
                }
            })
