from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.conf import settings
from bcauth.models import BCAuth
import bitcoinsig
import datetime

class BitcoinBackend(object):
    """
    Authenticate with a signed bitcoin message
    """

    def authenticate(self, username=None, response=None):
        print('authenticating')
        if None in (username, response):
            return None
        try:
            user = User.objects.get(username=username)
            try:
                bcauth = BCAuth.objects.get(username=username)
            except BCAuth.DoesNotExist:
                return None
            if not hasattr(user, 'useraddresses'):
                return None
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            difference = now - bcauth.created_at
            if difference.seconds > settings.BCAUTH_SESSION_EXPIRE:
                return None
            try:
                if not bitcoinsig.verify_message(
                        user.useraddresses.address,
                        response,
                        bcauth.challenge.encode('utf-8')):
                    return None
            except:  # This is bad, but it's how gribble does it. needs fixing
                return None
            bcauth.delete()
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
