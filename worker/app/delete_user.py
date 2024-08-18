import mysql.connector
from flask import request, render_template
from app import webapp
from passlib.hash import sha256_crypt
import boto3

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id='access key',
    aws_secret_access_key='secret key'
)

user_dict = {}

#function to delete a user
@webapp.route('/delete', methods=['GET', 'POST'])
def delete():
    user_to_delete = request.form.get('username')
    if user_to_delete == '':
        error_msg = 'Username should not be blank!'
        return render_template('delete_user.html', error_msg=error_msg)
        
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor= cred.cursor()
    cursor.execute("SELECT * FROM image_path;")
    user_list = [] 
    user_list_in_imagepath = []
    for (user,image_path) in cursor:
        user_list_in_imagepath.append(user)
    if user_to_delete in user_list_in_imagepath:
        delete_user_imagepath_query = "DELETE FROM image_path WHERE user = %s;"
        cursor.execute(delete_user_imagepath_query,(user_to_delete,))
        cred.commit()
    cursor.execute("SELECT * FROM user_accounts;")
    for (user,password,email,is_admin) in cursor:
        user_list.append(user)
    print(user_list)
    if user_to_delete in user_list:
        prefix = user_to_delete+"/"
        delete_user_query = "DELETE FROM user_accounts WHERE user = %s;"
        cursor.execute(delete_user_query,(user_to_delete,))
        cred.commit()
        bucket = s3.Bucket('assignment2ece1779')
        bucket.objects.filter(Prefix=prefix).delete()
        error_msg = "User "+ user_to_delete +" is successfully removed!"
        return render_template('delete_user.html', error_msg=error_msg)
    else:
        error_msg = "No User "+ user_to_delete +" is found!"
        return render_template('delete_user.html', error_msg=error_msg)
    cursor.close()
    cred.close()
        
