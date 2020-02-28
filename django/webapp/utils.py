from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger('webapp.utils')


def request_to_synagogue(request):
    if not request_has_synagogue(request):
        logger.info('user without synagogue approached')
        raise AuthenticationFailed("user doesn't have a synagogue")
    return request.user.usertosynagogue.synagogue


def request_has_synagogue(request):
    return hasattr(request, 'user') and hasattr(request.user, 'usertosynagogue')
