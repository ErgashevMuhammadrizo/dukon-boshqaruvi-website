"""Public website domain configuration; no wildcard host or API-domain substitution."""
import re
from urllib.parse import urlparse

WEBSITE_HOST = 'dukon-boshqaruvi-website-production.up.railway.app'
WEBSITE_URL = 'https://' + WEBSITE_HOST

def host(value):
    value = str(value).strip()
    if not value: return ''
    parsed = urlparse(value if '://' in value else '//' + value)
    hostname = parsed.hostname or ''
    if parsed.username or parsed.password or not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?', hostname):
        return ''
    return hostname.lower()

def configured_site_url(env):
    supplied = str(env.get('SITE_URL', '')).strip().rstrip('/')
    parsed = urlparse(supplied)
    if parsed.scheme == 'https' and host(supplied) and not parsed.query and not parsed.fragment and parsed.path in ('', '/'):
        return 'https://' + host(supplied)
    return WEBSITE_URL

def configured_hosts(env):
    candidates = [WEBSITE_HOST, 'localhost', '127.0.0.1', host(configured_site_url(env)),
        env.get('RAILWAY_PUBLIC_DOMAIN', ''), *env.get('ALLOWED_HOSTS', '').split(',')]
    return list(dict.fromkeys(value for value in (host(item) for item in candidates) if value))

def configured_origins(env):
    candidates = [WEBSITE_URL, configured_site_url(env)]
    railway = host(env.get('RAILWAY_PUBLIC_DOMAIN', ''))
    if railway: candidates.append('https://' + railway)
    for item in env.get('CSRF_TRUSTED_ORIGINS', '').split(','):
        value = item.strip().rstrip('/')
        parsed = urlparse(value)
        if parsed.scheme in ('https', 'http') and host(value) and not parsed.username and not parsed.password:
            candidates.append(value)
    return list(dict.fromkeys(candidates))
