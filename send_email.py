import smtplib

smtp_addr = "###"
user = "###"
pw = "###"
port = ###

def send_emails(to_array, subject, body):
    server = smtplib.SMTP(smtp_addr, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user, pw)
    message = f"Subject: {subject}\n\n{body}"
    for to in to_array:
        server.sendmail(user, to, message)
    server.close()
