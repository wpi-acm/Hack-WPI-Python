import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config_hackWPI import (api_keys)

user = api_keys['smtp_email']['user']
bcc = api_keys['smtp_email']['bcc']
reply = api_keys['smtp_email']['reply']
sender = api_keys['smtp_email']['sender']
smtp_server = api_keys['smtp_email']['smtp_server']
smtp_port = api_keys['smtp_email']['smtp_port']

def send_message(recipients, subject="", html="", text=""):
    print("Sending email to {0} with subject {1}".format(recipients, subject))
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg.add_header('reply-to', reply)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(smtp_server, smtp_port)
    # Enable TLS if we're using secure SMTP
    if(smtp_port > 25):
        server.starttls()
    # Login if we're using server with auth
    if ('pass' in api_keys['smtp_email']):
        server.login(user, api_keys['smtp_email']['pass'])

    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_message(["acm-sysadmin@wpi.edu"], "Test Subject", "<b>Test HTML</b>", "Test text")