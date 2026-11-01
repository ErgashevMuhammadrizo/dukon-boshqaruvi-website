"""Append-only website integration: never replaces the project's API URL file."""
from pathlib import Path
import os
import sys

def configure_website(namespace):
    root = Path(os.environ.get('WEBSITE_ROOT', '/website')).resolve()
    sys.path.insert(0, str(root.parent))
    apps = namespace['INSTALLED_APPS']
    if 'website.apps.WebsiteConfig' not in apps:
        apps.append('website.apps.WebsiteConfig')
    namespace['TEMPLATES'][0]['DIRS'].append(root / 'templates')
    namespace['TEMPLATES'][0]['APP_DIRS'] = True

def mount_website(patterns):
    from django.urls import include, path
    # Only the existing exact homepage is replaced; all /api/ routes are preserved.
    return [p for p in patterns if getattr(p.pattern, '_route', None) != ''] + [path('', include('website.urls'))]
