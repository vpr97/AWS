
file='/home/ubuntu/.aws/credentials' 

AWS_ACCESS_KEY_ID='AWS_ACCESS_KEY_ID'
AWS_SECRET_KEY='AWS_SECRET_KEY'


with open(file, 'w') as filetowrite:
    myCredential = f"""[default]
aws_access_key_id={AWS_ACCESS_KEY_ID}
aws_secret_access_key={AWS_SECRET_KEY}
"""
    filetowrite.write(myCredential)
    
    
    
    
#### Write in some default settings, don't change anything here 
file='/home/ubuntu/.aws/config' 
with open(file, 'w') as filetowrite:
    myCredential = """[default]
                      region = us-east-1
                      output = json
                      [profile prod]
                      region = us-east-1
                      output = json"""
    filetowrite.write(myCredential)
    
