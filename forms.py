from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.conf import settings
from bcauth.models import BCAuth, UserAddresses
from django.contrib.auth import authenticate, login, logout
import bitcoinsig
import datetime
import hashlib
import os


def get_challenge_string():
    now = datetime.datetime.utcnow()
    expires = now+datetime.timedelta(0, settings.BCAUTH_SESSION_EXPIRE)
    challenge_string = settings.BCAUTH_CHALLENGE
    challenge_string = challenge_string.replace(
        '$otp',
        hashlib.sha256(os.urandom(128)).hexdigest()[:-8]
    )
    challenge_string = challenge_string.replace(
        '$timestamp',
        now.strftime("%Y-%m-%d %H:%M:%S")
    )
    challenge_string = challenge_string.replace(
        '$expires',
        expires.strftime("%Y-%m-%d %H:%M:%S")
    )
    return challenge_string


def get_challenge(username):
    challenge = get_challenge_string()
    bcauth, created = BCAuth.objects.get_or_create(
        username=username,
        defaults={'challenge': challenge}
    )
    if not created:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        difference = now - bcauth.created_at
        if difference.seconds > settings.BCAUTH_SESSION_EXPIRE:
            print 'creating new timestamp'
            bcauth.challenge = challenge
            bcauth.created_at = now
            bcauth.save()
    return bcauth.challenge.encode('utf-8')


class BCRegisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BCRegisterForm, self).__init__(*args, **kwargs)

    username = forms.RegexField(
        widget=forms.HiddenInput(),
        label=_("Username"),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
             "@/./+/-/_ characters.")}
    )
    address = forms.RegexField(
        label="Bitcoin Address",
        max_length=34,
        min_length=26,
        regex=r'^[13][a-km-zA-HJ-NP-Z0-9]{26,33}$',
        help_text=_("Required."),
        error_messages={
            'invalid': _("Not a valid bitcoin address.")}
    )
    response = forms.CharField(max_length=128, min_length=26)

    def clean(self):
        username = self.cleaned_data.get('username')
        address = self.cleaned_data.get('address')
        response = self.cleaned_data.get('response')
        try:
            bcauth = BCAuth.objects.get(username=username)
        except BCAuth.DoesNotExist:
            raise forms.ValidationError('Sorry, that login was invalid. Please try again.')
        try:
            user = User.objects.get(username=username)
            if not self.user.is_authenticated() or user != self.user:
                raise forms.ValidationError('User already exists')
        except User.DoesNotExist:
            pass
        try:
            if not bitcoinsig.verify_message(
                    address,
                    response,
                    bcauth.challenge.encode('utf-8')):
                raise forms.ValidationError("Signature validation failed")
        except:
            raise forms.ValidationError("Signature validation failed. Invalid address or signature provided")
        return self.cleaned_data

    def register(self, request):
        username = self.cleaned_data.get('username')
        address = self.cleaned_data.get('address')
        try:
            user = User.objects.get(username=username)
            if not self.user.is_authenticated() or user != self.user:
                raise None
        except User.DoesNotExist:
            user = User.objects.create_user(username)
        UserAddresses.objects.create(
            user=user,
            address=address
        )
        return user

    def login(self, request):
        username = self.cleaned_data.get('username')
        response = self.cleaned_data.get('response')
        user = authenticate(username=username, response=response)
        return user


class BCChallengeForm(forms.Form):
    username = forms.RegexField(
        widget=forms.HiddenInput(),
        label=_("Username"),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
             "@/./+/-/_ characters.")}
    )
    response = forms.CharField(max_length=128, min_length=26)

    def clean(self):
        username = self.cleaned_data.get('username')
        response = self.cleaned_data.get('response')
        self.user = authenticate(username=username, response=response)
        if not self.user or not self.user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        return self.user

class UserForm(forms.Form):
    username = forms.RegexField(
        label=_("Username"),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
             "@/./+/-/_ characters.")}
    )
