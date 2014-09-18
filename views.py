from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.utils.timezone import utc
from django.contrib.auth.models import User
from django.views.generic import View
from bcauth.forms import (
    BCRegisterForm,
    BCChallengeForm,
    UserForm,
    get_challenge,
    get_challenge_string
)
from bcauth.models import BCAuth
from django.contrib.auth import login, logout
import datetime


class BCLoginView(View):
    form_class = UserForm
    initial = {}
    template_name = 'bcauth/login.html'

    def get(self, request, *args, **kwargs):
        userform = self.form_class(initial=self.initial)
        return render_to_response(
            self.template_name,
            {'form': userform},
            context_instance=RequestContext(request)
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
            except User.DoesNotExist:
                user = None
            request.session['_bcauth_username'] = form.cleaned_data['username']
            print user, hasattr(user, 'useraddresses')
            if user and hasattr(user, 'useraddresses'):
                return redirect('bcauth-challenge')
            else:
                return redirect('bcauth-register')
        userform = self.form_class(request.POST)
        return render_to_response(
            self.template_name,
            {'form': userform},
            context_instance=RequestContext(request)
        )


class BCChallengeView(View):
    form_class = BCChallengeForm
    initial = {}
    template_name = 'bcauth/challenge.html'

    def get(self, request, *args, **kwargs):
        username = request.session.get('_bcauth_username')
        self.initial['username'] = username
        form = self.form_class(initial=self.initial)
        return render_to_response(
            'bcauth/challenge.html',
            {
                'challenge': get_challenge(username),
                'form': form
            },
            context_instance=RequestContext(request)
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, initial=self.initial)
        if form.is_valid():
            user = form.login(request)
            if user:
                login(request, user)
                return render_to_response(
                    'bcauth/registered.html',
                    {},
                    context_instance=RequestContext(request)
                )
        username = request.session.get('_bcauth_username')
        return render_to_response(
            'bcauth/challenge.html',
            {
                'challenge': get_challenge(username),
                'form': form
            },
            context_instance=RequestContext(request)
        )


class BCRegisterView(View):
    form_class = BCRegisterForm
    initial = {}
    template_name = 'bcauth/register.html'

    def _setup_challenge(self, username):
        challenge_string = get_challenge_string()
        bcauth, created = BCAuth.objects.get_or_create(
            username=username,
            defaults={'challenge': challenge_string}
        )
        challenge_string = bcauth.challenge
        if not created:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            difference = now - bcauth.created_at
            if difference.seconds > settings.BCAUTH_SESSION_EXPIRE:
                bcauth.challenge = challenge_string
                bcauth.created_at = now
                bcauth.save()
        return bcauth.challenge

    def get(self, request, *args, **kwargs):
        username = request.session.get('_bcauth_username')
        self.initial['username'] = username
        form = self.form_class(initial=self.initial, user=request.user)
        return render_to_response(
            'bcauth/register.html',
            {
                'challenge': self._setup_challenge(username),
                'form': form
            },
            context_instance=RequestContext(request)
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST,
            initial=self.initial,
            user=request.user
        )
        if form.is_valid():
            form.register(request)
            user = form.login(request)
            login(request, user)
            return render_to_response(
                'bcauth/registered.html',
                {},
                context_instance=RequestContext(request)
            )
        username = request.session.get('_bcauth_username')
        return render_to_response(
            'bcauth/register.html',
            {
                'challenge': self._setup_challenge(username),
                'form': form
            },
            context_instance=RequestContext(request)
        )



def status(request):
    return render_to_response(
        'bcauth/registered.html',
        {},
        context_instance=RequestContext(request)
    )
