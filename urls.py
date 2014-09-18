from django.conf.urls import patterns, include, url
from bcauth.views import BCLoginView, BCChallengeView, BCRegisterView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bcauth_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^login/', BCLoginView.as_view(), name='bcauth-login'),
    url(r'^challenge/', BCChallengeView.as_view(), name='bcauth-challenge'),
    url(r'^register/', BCRegisterView.as_view(), name='bcauth-register'),
    url(r'^status/', 'bcauth.views.status'),
)
