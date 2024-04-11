import smtplib
from email.message import EmailMessage
import os
import random

# https://myaccount.google.com/apppasswords
gmail = 'yhlf mexm fafj vcvn'

def email_otp(email_to, username):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('rohithravi2015@gmail.com', gmail)

        otp = random.randint(1000, 9999)
        email = EmailMessage()
        email['Subject'] = 'SmartFare: Login with otp.'
        email['From'] = 'rohithravi2015@gmail.com'
        email['To'] = email_to
        email.set_content(f'''
        Hi {username},
        Your One Time Password (OTP) to Login on SmartFare is {otp}.
        Please note, this OTP is valid only for mentioned transaction 
        and cannot be used for any other transaction.
        Please do not share this One Time Password with anyone.
        
        Thank you
        
        ''')

        smtp.send_message(email)
        return otp


def booking_confirmation(username, email_to):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('rohithravi2015@gmail.com', gmail)

        # https://myaccount.google.com/apppasswords
        email = EmailMessage()
        email['Subject'] = 'SmartFare: Booking confirmation.'
        email['From'] = 'rohithravi2015@gmail.com'
        email['To'] = email_to
        email.set_content(f'''
        Hi {username},
        This is to confirm that you have successfully register yourself.
        
        Thank you

        ''')

        smtp.send_message(email)


def forgot_pwd_email(email_to, username):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('rohithravi2015@gmail.com', gmail)
        # https://myaccount.google.com/apppasswords
        otp = random.randint(1000, 9999)
        email = EmailMessage()
        email['Subject'] = 'One Time Password (OTP) for Forgot Password recovery on SmartFare App'
        email['From'] = 'rohithravi2015@gmail.com'
        email['To'] = email_to
        email.set_content(f'''
        Hi {username},
        Please login with below credentials to SmartFare.
        
        Username: {username}
        Password/OTP: {otp}
         
        Then proceed to 'Change Password' section to set new password of your choice. 
        
        This OTP is valid only for mentioned transaction and cannot be used for any other  transaction.
        
        Please do not share this One Time Password with anyone.

        Thank you

        ''')

        smtp.send_message(email)
        return otp








