"""
This documents allows us to serve different URL patterns depending on the
domain. This means that subdomains have their own routes.

Loosely based on https://code.djangoproject.com/wiki/MultiHostMiddleware
But that had to be rewritten because it was for a very old Django version

This was used in Metabolism of Cities to select the project (site) that was
being opened. No longer relevant so hard coded to project=17. In due course
the whole project element could be removed, but not a priority now.
If desired, multi-language can be configured - kept the code for that if 
at some point a translated version of the site is of interest.

"""

from django.conf import settings
from django.urls import set_urlconf
from django.utils import translation

class MultiHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        project = 17
        host = request.META.get("HTTP_HOST")

        if "django_language" in request.COOKIES:
            language_code = request.COOKIES.get("django_language")
        else:
            language_code = "en"

        translation.activate(language_code)
        request.language = language_code
        request.project = project
        response = self.get_response(request)

        return response
