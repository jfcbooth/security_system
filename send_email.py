import smtplib
import shutil
import os

apache_media_dir = "C:\Apache24\htdocs\media\"

def send_email(category, file_loc):
categories = {'0': 'none', '1': 'animal', '2': 'person', '3': 'vehicle'}
gmail_user = 'boothcamerasystem@gmail.com'
gmail_password = 'grizzly2000'

FROM = gmail_user
TO = 'boothcrap@gmail.com'

SUBJECT = 'identified'
shutil.copy(file_loc, os.path.join(apache_media_dir, categories[str(category)])) # move 

if(categories == 2):
    SUBJECT = 'person ' + subject
if(category == 3):
    SUBJECT = 'vehicle' + subject

body = 'Test email content'

message = 'Subject: {}\n\n{}'.format(SUBJECT, body)

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(FROM, TO, message)
    server.close()

    print('Email sent.')
except:
    print('Error: Email not sent.')