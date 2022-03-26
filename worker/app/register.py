import mysql.connector
from flask import request, render_template
from app import webapp
from passlib.hash import sha256_crypt
import boto3

s3 = boto3.client(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id='AKIA5GURIKZLXOWNVEFZ',
    aws_secret_access_key='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'
)

user_dict = {}

#function to create a new user
@webapp.route('/register', methods=['GET', 'POST'])
def register():
    new_user = request.form.get('username')
    new_password = request.form.get('password')
    new_enc_password = sha256_crypt.encrypt(new_password)
    new_repassword = request.form.get('repassword')
    new_is_admin = False

    new_mail = request.form.get('mail')
    if new_user == '':
        error_msg = 'Username should not be blank!'
        return render_template('register_new_user.html', error_msg=error_msg)
    if new_password == '':
        error_msg = 'Password should not be blank!'
        return render_template('register_new_user.html', error_msg=error_msg)
    if new_mail == '':
        error_msg = 'Email should not be blank!'
        return render_template('register_new_user.html', error_msg=error_msg)

    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")

    for (user, password, email, is_admin) in cursor:
        user_dict[user] = password
    if new_user in user_dict.keys():
        error_msg = "User already exists!"
        return render_template('register_new_user.html', error_msg=error_msg)
    elif len(new_user)>100:
        error_msg = "Username length should not be greater than 100"
        return render_template('register_new_user.html', error_msg=error_msg)
    else:
        if new_password == new_repassword:
            add_user = ("INSERT INTO user_accounts VALUES (%s, %s, %s, %s);")
            cursor.execute(add_user, (new_user, new_enc_password, new_mail, new_is_admin,))
            cred.commit()
            error_msg = 'Used added Successfully!'
            
            #creating a folder in S3
            
            bucket_name = "assignment2ece1779"
            directory_name = new_user
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/'))
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/thumb/'))
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/transform/'))
            
            return render_template('register_new_user.html', error_msg=error_msg)
        else:
            error_msg = 'Password does not match!'
            return render_template('register_new_user.html', error_msg=error_msg)

    cursor.close()
    cred.close()
