import random
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters


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


def send_password_reset_to_user(user_email,  uid, token, domain='127.0.0.1:8000', use_https=False):
    protocol = 'https' if use_https else 'http'
    url = reverse('password_reset_confirm', kwargs={'uid': uid, 'token': token})
    message = f'{protocol}://{domain}{url}'

    subject = 'email to reset password'

    send_mail(
        subject,
        message,
        settings.EMAIL_FROM,
        [user_email]
    )


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password', 'password2', 'new_password', 'new_password2')
)
