import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_mail(email, title, html, context, from_email="noreply@yaamod.co.il"):
    logging.info('sending email to {0}'.format(email))

    email_html_message = render_to_string(html, context)
    msg = EmailMultiAlternatives(title, from_email=from_email, to=email)
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
