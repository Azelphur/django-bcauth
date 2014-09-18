from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import datetime

# Create your models here.
class BCAuth(models.Model):
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
            '@/./+/-/_ only.')
    )
    challenge = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)


class UserAddresses(models.Model):
    user = models.OneToOneField(User)
    address = models.CharField(max_length=50, unique=True)
