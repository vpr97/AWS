import mysql.connector
from flask import request, render_template
from passlib.hash import sha256_crypt
from app import webapp
from flask_mail import Mail, Message

webapp.config['MAIL_SERVER'] = 'smtp.gmail.com'
webapp.config['MAIL_PORT'] = 587
webapp.config['MAIL_USERNAME'] = 'ece1779flaskproject@gmail.com'
webapp.config['MAIL_PASSWORD'] = 'ece1779flask'
webapp.config['MAIL_USE_TLS'] = True
webapp.config['MAIL_USE_SSL'] = False
mail = Mail(webapp)

user_dict = {}

#function to navigate to forgot password page
@webapp.route('/gotorecoverpassword')
def recover_password():
    return render_template('forgot_password.html')

#function to send mail to user's email id to recover password
@webapp.route("/recoverpassword", methods=['GET', 'POST'])
def mail_body():
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")

    for (user, password, email, is_admin) in cursor:
        user_dict[user] = email

    cursor.close()
    cred.close()
    
    global n1,n2;

    n1 = request.form.get('username')
    n2 = request.form.get('mail')
    
    if n1 == '' or n2 == '':
        error_msg = "Username or Mail should not be blank!"
    
    elif n1 in user_dict.keys():
        if n2 == user_dict[n1]:
            msg = Message('Reset Password', sender='ece1779flaskproject@gmail.com', recipients=[request.form.get('mail')])
            msg.html = render_template('/mail_link.html', username=n1)
            mail.send(msg)
            error_msg = "Mail sent Successfully."
        
        else:
            error_msg = "Mail does not match with user."
            
    else:
        error_msg = "User does not exist."
        
        
        
    return render_template('forgot_password.html', error_msg=error_msg)

#function to display reset password page
@webapp.route('/go_to_reset_password_page', methods=["GET"])
def go_to_reset_password_page():
    return render_template('reset_password_email.html')

#function to update the password in the database
@webapp.route("/resetpassword", methods=['GET', 'POST'])
def reset_password():
    new_password = request.form.get('password')
    new_enc_password = sha256_crypt.encrypt(new_password)
    username = request.form.get('username')
    if username == '':
        error_msg = "Username field should not be blank."
        
    if (username == n1):
        cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
        cursor = cred.cursor()
        query = "UPDATE user_accounts set password = %s  where user = %s;"
        cursor.execute(query, (new_enc_password, username,))
        cred.commit()
        cursor.close()
        cred.close()

        error_msg = "Password updated Successfully."
    else:
        error_msg = "The user is not authorised to change the password."
        
    return render_template('/reset_password_email.html', error_msg=error_msg)
