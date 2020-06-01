import os, sys
sys.path.append('%(path_to_django)s')
sys.path.append('%(path_to_project)s')
os.environ['DJANGO_SETTINGS_MODULE'] = '%(project)s.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
