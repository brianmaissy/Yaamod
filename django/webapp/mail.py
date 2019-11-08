import logging
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string

logger = logging.Logger('mail')


def send_mail(email, title, html, context, from_email="noreply@yammod.co.il"):
    logger.info('sending email to {0}'.format(email))

    email_html_message = render_to_string(html, context)
    django_send_mail(title, '', from_email, [email], html_message=email_html_message)
