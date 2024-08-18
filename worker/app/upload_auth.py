import os
import urllib

import mysql.connector
from flask import request, render_template, session
from werkzeug.utils import secure_filename
from PIL import Image as Image1
from wand.image import Image
from passlib.hash import sha256_crypt
import random
import string
import urllib.request
import boto3



from app import webapp

s3 = boto3.client(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id='access key',
    aws_secret_access_key='secret key'
)

UPLOAD_FOLDER = '/home/ubuntu/assignment2/app/static/uploads'
print(UPLOAD_FOLDER)
webapp.secret_key = "secret key"
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webapp.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
user_thumb_images = []
user_transform_images = []

#function to verify the allowed extensions of the image that can be uploaded
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#function to verify the format of the uploaded image
def file_format(filename):
    imageformat = filename.rsplit('.', 1)[1]
    format = {
        "png": ".png",
        "jpg": ".jpg",
        "jpeg": ".jpeg",
        "gif": ".gif",
        "PNG": ".PNG",
        "JPG": ".JPG",
        "JPEG": ".JPEG",
        "GIF": ".GIF"
    }
    return format[imageformat]


user_dict = {}

#function to navigate to upload image screen
@webapp.route('/gotouploadpage')
def go_to_upload_page():
    return render_template('upload_file.html')

#function to upload image, also transformation is done here and the transformed images are saved
@webapp.route('/upload', methods=['GET', 'POST'])
def upload():
    user_session = session["user"]
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")

    for (user, password, email, is_admin) in cursor:
        user_dict[user] = password

    cursor.close()
    cred.close()
    path_extract_tuple = []
    path_extract = []
    all_uploaded_images = []

    n1 = request.form.get('username')
    n2 = request.form.get('password')
    webimage_url = request.form.get('web_image')
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
        error_msg = 'Username or Password cannot be empty!'
        return render_template('upload_file.html', error_msg=error_msg)

    if "user" in session:
        if session["user"] == n1:
            if n1 in user_dict.keys():
                if sha256_crypt.verify(n2, user_dict[n1]):
                    if webimage_url:
                       
                        namewithslash = (webimage_url.split('/'))[-1]
                        format = file_format(namewithslash)
                        letters = string.ascii_lowercase
                        random_name = (''.join(random.choice(letters) for i in range(6)))
                        save_webimage_path = "/home/ubuntu/assignment2/app/static/uploads/" + random_name + format
                        filename = (save_webimage_path.split('/'))[-1]
                        urllib.request.urlretrieve(webimage_url,save_webimage_path)
                        
                        user_session = session["user"]
                        s3_storage_path = user_session+"/transform/"+random_name + format
                        s3.upload_file(save_webimage_path,'assignment2ece1779',s3_storage_path)
                        
                        thumb_name_list = filename.split(".")
                        thumb_extract = thumb_name_list[0]
                        THUMB_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_thumb'+ format
                        thumb_list = THUMB_FOLDER.split("/")
                        thumb_name = thumb_list[-1]
                        
                        THUMB_s3 = user_session + '/thumb/' + thumb_extract + '_thumb' + format
                        thumb = Image1.open(save_webimage_path)
                        MAX_SIZE = (100, 100)
                        thumb.thumbnail(MAX_SIZE)
                        thumb.save(THUMB_FOLDER)
                        s3.upload_file(THUMB_FOLDER,'assignment2ece1779',THUMB_s3)
                        
       
                        BLUR_s3 = user_session + '/transform/' + thumb_extract + '_blur' + format
                        blur_image = Image(filename=save_webimage_path)
                        BLUR_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_blur'+ format
                        blur_list = BLUR_FOLDER.split("/")
                        blur_name = blur_list[-1]
                        blur_image.blur(radius=0, sigma=8)
                        blur_image.save(filename=BLUR_FOLDER)
                        s3.upload_file(BLUR_FOLDER,'assignment2ece1779',BLUR_s3)
                        
                      
                        SHADE_s3 = user_session + '/transform/' + thumb_extract + '_shade' + format
                        shade_image = Image(filename=save_webimage_path)
                        SHADE_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_shade'+ format
                        shade_list = SHADE_FOLDER.split("/")
                        shade_name = shade_list[-1]
                        shade_image.shade(gray=True, azimuth=286.0, elevation=45.0)
                        shade_image.save(filename=SHADE_FOLDER)
                        s3.upload_file(SHADE_FOLDER,'assignment2ece1779',SHADE_s3)

                        SPREAD_s3 = user_session + '/transform/' + thumb_extract + '_spread' + format
                        spread_image = Image(filename=save_webimage_path)
                        SPREAD_FOLDER = UPLOAD_FOLDER + '/' + thumb_extract + '_spread'+ format
                        spread_list = SPREAD_FOLDER.split("/")
                        spread_name = spread_list[-1]
                        spread_image.spread(radius=8)
                        spread_image.save(filename=SPREAD_FOLDER)
                        s3.upload_file(SPREAD_FOLDER,'assignment2ece1779',SPREAD_s3)

                        cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
                        cursor = cred.cursor()
                        query = ("INSERT INTO image_path VALUES(%s,%s);")
                        cursor.execute(query, (n1, save_webimage_path,))
                        cred.commit()
                        cursor.close()
                        cred.close()

                        error_msg = 'Image successfully uploaded!'
                        return render_template('upload_file.html', error_msg=error_msg)
                    else:
                        if request.method == "POST":
                            if 'image' not in request.files:
                                error_msg = 'No file part!'
                                return render_template('upload_file.html', error_msg=error_msg)
                            image = request.files['image']
                            if image.filename == '':
                                error_msg = 'No image selected for uploading!'
                                return render_template('upload_file.html', error_msg=error_msg)
                            if image and allowed_file(image.filename):
                                filename = secure_filename(image.filename)
                                if filename in all_uploaded_images:
                                    letters = string.ascii_lowercase
                                    random_name = (''.join(random.choice(letters) for i in range(6)))
                                    filename = filename.split('.')[0]
                                    image_format = file_format(image.filename)
                                    filename = filename + '_' + random_name + image_format
                                    image.save(os.path.join(webapp.config['UPLOAD_FOLDER'], filename))
                                    imagepath = UPLOAD_FOLDER + '/' + filename


                                else:
                                    image.save(os.path.join(webapp.config['UPLOAD_FOLDER'], image.filename))
                                    # s3.Bucket('assignment2ece1779').upload_file(Filename=image.filename,Key=image.filename)
                                    user_session = session["user"]
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
                                thumb_obj = thumb.thumbnail(MAX_SIZE)
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

                                error_msg = 'Image successfully uploaded!'
                                return render_template('upload_file.html', error_msg=error_msg)
                            else:
                                error_msg = 'Allowed image types are - png, jpg, jpeg, gif!'
                                return render_template('upload_file.html', error_msg=error_msg)
                else:
                    error_msg = "Wrong Password!"
                    return render_template('upload_file.html', error_msg=error_msg)
            else:
                error_msg = "User does not exist!"
                return render_template('upload_file.html', error_msg=error_msg)
        else:
            error_msg = "Use Active User Credentials!"
            return render_template('upload_file.html', error_msg=error_msg)

#function to view the thumbnails of the all the uploaded images by that particular user
@webapp.route('/displayViewThumbnail', methods=["POST", "GET"])
def display_thumbnail_image():
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")

    for (user, password, email, is_admin) in cursor:
        user_dict[user] = password

    n1 = request.form.get('username')
    n2 = request.form.get('password')
    webimage_url = request.form.get('web_image')
    cursor.close()
    cred.close()

    if n1 == "" or n2 == "":
        error_msg = 'Username or Password cannot be empty!'
        return render_template('upload_file.html', error_msg=error_msg)

    path_extract_tuple = []
    path_extract = []
    if "user" in session:
        n1 = session["user"]
        if n1 in user_dict.keys():
            if sha256_crypt.verify(n2, user_dict[n1]):
                
                contents = show_image('assignment2ece1779')
                
                #print(contents)
                for element in contents:
                    if n1 in element:
                        element_splist = element.split("/")
                        if ((element_splist[-1]).startswith('?')):
                            pass
                        else:
                            if (element_splist[-2]== 'thumb'):
                                user_thumb_images.append(element)
                            elif (element_splist[-2]== 'transform'):
                                user_transform_images.append(element)
                #print(user_images)            
                return render_template('thumbnail.html', user_thumb_images=user_thumb_images)
            else:
                error_msg = "Wrong Password!"
                return render_template('upload_file.html', error_msg=error_msg)
        else:
            error_msg = "User does not exist!"
            return render_template('upload_file.html', error_msg=error_msg)
    else:
        error_msg = "Use Active User Credentials!"
        return render_template('upload_file.html', error_msg=error_msg)
# function to display the transformations of the selected image
# @webapp.route('/view_transformation/<item>')
# def view_transformation(item):
#     name = item.split('_')
#     picture_name = name[0]
#     format = file_format(name[-1])
#     normal_name = picture_name + format
#     blur_name = picture_name + "_blur" + format
#     shade_name = picture_name + "_shade" + format
#     spread_name = picture_name + "_spread" + format

@webapp.route('/view_transformation/<image_name>')
def view_transformation(image_name):
    
    user = session['user']
    user_display_image_list = []
    display_image_list = []
    getImageName = image_name
    for image in user_transform_images:
        if user in image:
            user_display_image_list.append(image)
    for element in user_display_image_list:
        if getImageName in element:
            display_image_list.append(element)
    print(display_image_list)
    for element in display_image_list:
        if "blur" in element:
            blur_name = element
        elif "shade" in element:
            shade_name = element
        elif "spread" in element:
            spread_name = element
        else:
            normal_name = element
            
    return render_template("view_transformation.html", normal_name=normal_name, blur_name=blur_name,
                           shade_name=shade_name, spread_name=spread_name)

def show_image(bucket):
    public_urls = []
    n1 = session["user"]
    prefix = n1 + "/"
    try:
        for item in s3.list_objects(Bucket=bucket)['Contents']:
            presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 10000)
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    # print("[INFO] : The contents inside show_image = ", public_urls)
    #, 'Prefix': prefix, delimiter: '/'
    return public_urls
    # fullpath_thumb_list = []
                # cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
                # cursor = cred.cursor(buffered=True)
                # query = ("SELECT path from image_path where user = %s;")
                # cursor.execute(query, (str(n1),))
                # for row in cursor:
                #     path_extract_tuple.append(row)

                # cursor.close()
                # cred.close()
                # for path in path_extract_tuple:
                #     path_extract.append(''.join(path))
                
                # for fullpath in path_extract:
                #     fullpath_list = fullpath.split('/')

                #     fullpath_thumb = (fullpath_list[-1])
                #     format = file_format(fullpath_thumb)
                #     fullpath_thumbname = (fullpath_thumb.split('.'))[0] + '_thumb' + format
                #     fullpath_thumb_list.append(fullpath_thumbname)
                # fullpath_thumb_list=fullpath_thumb_list
