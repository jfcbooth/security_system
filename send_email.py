from functools import total_ordering
import smtplib
import shutil
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(category_name, video_file_loc):
    msg_to = 'boothcrap@gmail.com'
    msg_from = 'boothcamerasystem@gmail.com'
    gmail_password = 'grizzly2000'
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')

    msg['From'] = msg_to
    msg['To'] = msg_from

    if(category_name == 'animal'):
        msg['Subject'] = 'Animal Identified'
    elif(category_name == 'person'):
        msg['Subject'] = 'Person Identified'
    elif(category_name == 'vehicle'):
        msg['Subject'] = 'Vehicle Identified'
    else:
        msg['Subject'] = 'Error: Nothing detected. Please report to sysadmin'

    # Create the body of the message (a plain-text and an HTML version).
    text = "Video viewable at: {}".format(video_file_loc)
    html = """\
    <html>
    <head></head>
    <body>
        <p>Video viewable at: <a href="{0}">{0}</a>
        </p>
    </body>
    </html>
    """.format(video_file_loc)

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
    send_email('animal', 'localhost/animal/my_test.webm')