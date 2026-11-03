"""
WSGI config for lingua project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lingua_backend.config.settings")

application = get_wsgi_application()
