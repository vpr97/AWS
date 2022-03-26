import mysql.connector
from flask import request, render_template, session
from passlib.hash import sha256_crypt
from app import webapp
import pymssql




user_dict = {}

#function reads the avaiable data from the database
@webapp.route('/', methods=['GET', 'POST'])
def login():
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    cursor.execute("SELECT * FROM user_accounts;")

    for (user, password, email, is_admin) in cursor:
        user_dict[user] = password

    cursor.close()
    cred.close()

    return render_template("login_page.html")

#function to verify login functionality
@webapp.route('/home', methods=['GET', 'POST'])
def home_func():
    n1 = request.form.get('username')
    n2 = request.form.get('password')
    session["user"] = n1

    if n1 == '' or n2 == '':
        error_msg = "Username or Password should not be blank!"
        return render_template('login_page.html', error_msg=error_msg)
    if n1 in user_dict.keys():
        if sha256_crypt.verify(n2, user_dict[n1]):
            return render_template('home.html', username=n1)
        else:
            error_msg = "Wrong Password!"
            return render_template('login_page.html', error_msg=error_msg)
    else:
        error_msg = "User does not exist!"
        return render_template('login_page.html', error_msg=error_msg)
    
#function to navigate to register user page (only admit will be able to create a new user)
@webapp.route('/create_user', methods=['GET', 'POST'])
def admin_login():
    n1 = request.form.get('username')
    n2 = request.form.get('password')

    if n1 == '' or n2 == '':
        error_msg = "Username or Password should not be blank!"
        return render_template('login_page.html', error_msg=error_msg)
    
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    query = "SELECT * FROM user_accounts where user = %s;"
    cursor.execute(query, (n1,))
    row = cursor.fetchone()
    flag = row[3]

    if n1 in user_dict.keys():
        if sha256_crypt.verify(n2, user_dict[n1]):
            if flag == 1:
                return render_template("register_new_user.html")
            else:
                error_msg = "User does not have permission to create a new account!"
                return render_template('login_page.html', error_msg=error_msg)
        else:
            error_msg = "Wrong Password."
            return render_template('login_page.html', error_msg=error_msg)
    else:
        error_msg = "User does not exist."
        return render_template('login_page.html', error_msg=error_msg)
        

#function to navigate to delete user page (only admit will be able to delete a user)
@webapp.route('/delete_user', methods=['GET', 'POST'])
def admin_deleteuser_login():
    n1 = request.form.get('username')
    n2 = request.form.get('password')

    if n1 == '' or n2 == '':
        error_msg = "Username or Password should not be blank!"
        return render_template('login_page.html', error_msg=error_msg)
    
    cred = mysql.connector.connect(user='root', password='ece1779pass', database='assignment2',host = 'assignment2.cjo1jsoigygz.us-east-1.rds.amazonaws.com', auth_plugin='mysql_native_password')
    cursor = cred.cursor()
    query = "SELECT * FROM user_accounts where user = %s;"
    cursor.execute(query, (n1,))
    row = cursor.fetchone()
    flag = row[3]

    if n1 in user_dict.keys():
        if sha256_crypt.verify(n2, user_dict[n1]):
            if flag == 1:
                return render_template("delete_user.html")
            else:
                error_msg = "User does not have permission to delete a user!"
                return render_template('login_page.html', error_msg=error_msg)
        else:
            error_msg = "Wrong Password."
            return render_template('login_page.html', error_msg=error_msg)
    else:
        error_msg = "User does not exist."
        return render_template('login_page.html', error_msg=error_msg)



