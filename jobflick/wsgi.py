import sys
import os

path = '/home/YOUR_USERNAME/jobflick-platform'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobflick.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
