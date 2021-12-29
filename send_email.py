import smtplib

gmail_user = 'boothcamerasystem@gmail.com'
gmail_password = 'grizzly2000'

FROM = gmail_user
TO = 'boothcrap@gmail.com'
SUBJECT = 'Human Detected Test'
body = 'Test email content'

message = 'Subject: {}\n\n{}'.format(SUBJECT, body)
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(FROM, TO, message)
    server.close()

    print('Email sent!')
except:
    print('Something went wrong...')