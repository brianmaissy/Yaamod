from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
import logging
from webapp.mail import send_mail


logger = logging.Logger('signals')


@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
    logger.info('got password reset request for {0}'.format(reset_password_token.user.email))

    # send an e-mail to the user
    context = {
        'username': reset_password_token.user.username,
        # TODO: make this a real endpoint, and build the url with reverse() rather than hard-coding it
        'reset_password_url': "https://yaamod.co.il/reset/?token={token}".format(token=reset_password_token.key)
    }

    send_mail(reset_password_token.user.email,
              u"החלפת סיסמא לאתר יעמוד",
              'webapp/password_reset.html',
              context)
