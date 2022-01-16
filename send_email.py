from functools import total_ordering
import smtplib
import shutil
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser

def send_email(category_name, video_file_loc, detections_file_loc, email_config):
    msg_to = email_config['to']
    msg_from = email_config['from']
    gmail_password = email_config['password']
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')

    msg['From'] = msg_from
    msg['To'] = msg_to

    if(category_name == 'animal'):
        msg['Subject'] = 'Animal Identified - {}'.format(os.path.basename(video_file_loc))
    elif(category_name == 'person'):
        msg['Subject'] = 'Person Identified - {}'.format(os.path.basename(video_file_loc))
    elif(category_name == 'vehicle'):
        msg['Subject'] = 'Vehicle Identified - {}'.format(os.path.basename(video_file_loc))
    else:
        msg['Subject'] = 'Error: Nothing detected. Please report to sysadmin'

    # Create the body of the message (a plain-text and an HTML version).
    text = "Video viewable at: {0}\nVideo with detections outlined viewable at: {1}".format(video_file_loc, detections_file_loc)
    html = """\
    <html>
    <head></head>
    <body>
        <p>Video viewable at: <a href="{0}">{0}</a></p>
        <p>Video with detections outlined viewable at: <a href="{1}">{1}</a></p>
    </body>
    </html>
    """.format(video_file_loc, detections_file_loc)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(msg_from, gmail_password)
        server.sendmail(msg_from, msg_to, msg.as_string())
        server.close()

        print('Email sent.')
    except:
        print('Error: Email not sent.')

if __name__ == "__main__":
    send_email('animal', 'localhost/animal/my_test.mp4', 'localhost/animal/detections/my_test_detections.mp4')