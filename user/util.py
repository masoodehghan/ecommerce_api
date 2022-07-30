import random
from django.conf import settings
from django.core.mail import send_mail


def send_email_to_user(user_email, pass_code):
    subject = 'Your Verification Code'
    body = f'Code: \n {pass_code}'

    send_mail(

        subject,
        body,
        settings.EMAIL_FROM,
        (user_email, )
    )


def generate_and_send_code(receiver_email):
    code = str(random.randint(10000, 99999))
    print('pass_code: ', code)
    return code
