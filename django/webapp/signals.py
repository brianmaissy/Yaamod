from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging


@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
    logging.info('got password reset request for {0}'.format(reset_password_token.user.email))

    # send an e-mail to the user
    context = {
        'username': reset_password_token.user.username,
        # TODO: make this a real endpoint
        'reset_password_url': "https://yaamond.co.il/reset/?token={token}".format(token=reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('webapp/password_reset.html', context)

    msg = EmailMultiAlternatives(
        # title:
        u"החלפת סיסמא לאתר יעמוד",
        # message:
        u'החלפת סיסמא באתר יעמוד!',
        # from:
        "noreply@yammod.co.il",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
