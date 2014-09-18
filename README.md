django-bcauth
=============

Bitcoin authentication for django, based on gribble.

Demo
=============
![](https://dl.dropboxusercontent.com/u/3832397/screenshots/2014/Sep/output_M6zNij.gif)

Installation
=============
In settings.py...

Add bcauth to your INSTALLED_APPS

Add bcauth.backends.BitcoinBackend to your AUTHENTICATION_BACKENDS

set BCAUTH_CHALLENGE to something sensible, like this.

BCAUTH_CHALLENGE = 'This message is being signed solely to authenticate to myWebsite on $timestamp. It is not to be used for any other purposes. It is void for any purpose after $expires. $otp'

set BCAUTH_SESSION_EXPIRE to the number of seconds to expire a login request in, 600 is recommended.

BCAUTH_SESSION_EXPIRE = 600
