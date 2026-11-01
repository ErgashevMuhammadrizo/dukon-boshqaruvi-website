"""Public product website; contacts and releases are managed through Django admin."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.views.static import serve

ROOT = Path(__file__).resolve().parent
APK_PATH = ROOT / 'public/downloads/dokon-boshqaruv.apk'
MISSING_APK = 'Ilova fayli hozircha joylanmagan. Iltimos, keyinroq qayta urinib ko‘ring.'

def configuration():
    defaults = {'product_name': 'e-dukon', 'download_url': '/downloads/dokon-boshqaruv.apk', 'apk_version': '', 'telegram_url': '', 'phone': '', 'email': ''}
    try:
        values = json.loads((ROOT / 'site_config.json').read_text())
    except (FileNotFoundError, ValueError):
        values = {}
    result = {k: str(values.get(k, v)).strip() for k, v in defaults.items()}
    from .models import SiteSettings
    from django.db.utils import OperationalError, ProgrammingError
    from django.conf import settings
    try:
        saved = SiteSettings.objects.filter(pk=1).first()
    except (OperationalError, ProgrammingError):
        saved = None
    result.update(contact_title='Biznesingiz haqida gaplashamiz.',
        contact_text='Savolingiz bormi? Sizga qulay kanalda yozing.',deals_url='',
        windows_url='', windows_version='', windows_available=False)
    if saved:
        for name in ['telegram_url','phone','email','contact_title','contact_text','deals_url','windows_version']:
            result[name] = getattr(saved,name)
        if saved.android_version: result['apk_version'] = saved.android_version
        result['windows_url'] = saved.windows_url
        if saved.windows_file:
            try:
                result['windows_available'] = saved.windows_file.storage.exists(saved.windows_file.name)
            except OSError: pass
            if result['windows_available']: result['windows_url'] = '/downloads/e-dukon-setup.exe'
        elif saved.windows_url: result['windows_available'] = True
    url = urlparse(result['download_url'])
    if not (result['download_url'].startswith('/') and not result['download_url'].startswith('//')) and not (url.scheme == 'https' and url.netloc):
        result['download_url'] = defaults['download_url']
    telegram = urlparse(result['telegram_url'])
    if telegram.scheme != 'https' or telegram.hostname not in ('t.me', 'telegram.me'):
        result['telegram_url'] = ''
    if not re.fullmatch(r'[+0-9 ()-]{7,30}', result['phone']): result['phone'] = ''
    result['phone_href'] = re.sub(r'[^+0-9]', '', result['phone'])
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', result['email']): result['email'] = ''
    for key in ['deals_url','windows_url']:
        parsed = urlparse(result[key])
        local = key == 'windows_url' and result[key] == '/downloads/e-dukon-setup.exe'
        if result[key] and not local and (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password):
            result[key] = ''
    if not result['windows_url']: result['windows_available'] = False
    result['has_contacts'] = any(result[k] for k in ('telegram_url', 'phone', 'email'))
    return result

def unavailable_apk():
    response = JsonResponse({'code': 'apk_unavailable', 'message': MISSING_APK}, status=404)
    response['Cache-Control'] = 'no-store'
    return response

def context(request, page):
    from django.conf import settings
    from .domain import WEBSITE_URL
    origin = getattr(settings, 'SITE_URL', WEBSITE_URL).rstrip('/')
    return {'site': configuration(), 'page': page,
        'canonical': origin + request.path,
        'og_image': origin + '/static/site/og.png'}

@require_safe
def home(request):
    return render(request, 'index.html', context(request, 'home'))

@require_safe
def download_page(request):
    return render(request, 'download.html', context(request, 'download'))

@require_safe
def apk_download(request):
    if not APK_PATH.is_file():
        return unavailable_apk()
    try:
        file = APK_PATH.open('rb')
    except OSError:
        return unavailable_apk()
    if file.read(4) != b'PK\x03\x04':
        file.close()
        return unavailable_apk()
    file.seek(0)
    response = FileResponse(file, as_attachment=True, filename='dokon-boshqaruv.apk', content_type='application/vnd.android.package-archive')
    response['Cache-Control'] = 'no-cache, must-revalidate'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

@require_safe
def asset(request, path):
    response = serve(request, path, document_root=ROOT / 'static/site')
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'public, max-age=3600'
    return response

def not_found(request, exception):
    return render(request, '404.html', context(request, 'error'), status=404)

@require_safe
def windows_download(request):
    from .models import SiteSettings
    saved = SiteSettings.objects.filter(pk=1).first()
    if saved and saved.windows_file:
        try:
            file = saved.windows_file.open('rb')
            if file.read(2) != b'MZ':
                file.close()
                raise OSError('Invalid executable')
            file.seek(0)
            response = FileResponse(file, as_attachment=True, filename='e-dukon-setup.exe', content_type='application/octet-stream')
            response['X-Content-Type-Options'] = 'nosniff'
            response['Cache-Control'] = 'no-cache'
            return response
        except (OSError, ValueError): pass
    return JsonResponse({'code':'windows_unavailable','message':'Windows o‘rnatuvchisi hali joylanmagan.'}, status=404)
