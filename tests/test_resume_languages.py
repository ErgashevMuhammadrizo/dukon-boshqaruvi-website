from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.test import TestCase, override_settings
from website import views
from website.templatetags.website_text import CATALOG

@override_settings(ALLOWED_HOSTS=['testserver'])
class ResumeLanguageTests(TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.apk=Path(self.tmp.name)/'release.apk'
        self.payload=b'PK\x03\x04'+bytes(range(256))*16
        self.apk.write_bytes(self.payload)
        self.patcher=patch.object(views,'APK_PATH',self.apk);self.patcher.start();self.addCleanup(self.patcher.stop)
    def body(self,r):
        b=b''.join(r.streaming_content);r.close();return b
    def test_resume_reconstructs_identical_apk(self):
        url='/downloads/dokon-boshqaruv.apk'
        h=self.client.head(url);self.assertEqual(h['Accept-Ranges'],'bytes');tag=h['ETag'];h.close()
        first=self.client.get(url,HTTP_RANGE='bytes=0-999',HTTP_IF_RANGE=tag)
        self.assertEqual(first.status_code,206);self.assertEqual(first['Content-Length'],'1000')
        rest=self.client.get(url,HTTP_RANGE='bytes=1000-',HTTP_IF_RANGE=tag)
        self.assertEqual(rest.status_code,206)
        self.assertEqual(self.body(first)+self.body(rest),self.payload)
    def test_suffix_clamp_and_invalid_ranges(self):
        url='/downloads/dokon-boshqaruv.apk'
        self.assertEqual(self.body(self.client.get(url,HTTP_RANGE='bytes=-20')),self.payload[-20:])
        self.assertEqual(self.body(self.client.get(url,HTTP_RANGE='bytes=4000-99999')),self.payload[4000:])
        for value in ['bytes=99999-','bytes=8-2','bytes=-0','bytes=0-1,4-8','bytes=-','bytes='+'9'*5000+'-']:
            r=self.client.get(url,HTTP_RANGE=value);self.assertEqual(r.status_code,416,value[:50]);self.assertIn('Content-Range',r)
    def test_changed_release_does_not_mix_bytes(self):
        r=self.client.get('/downloads/dokon-boshqaruv.apk',HTTP_RANGE='bytes=100-',HTTP_IF_RANGE='"old-build"')
        self.assertEqual(r.status_code,200);self.assertEqual(self.body(r),self.payload)
    def test_download_never_redirects_to_external_file(self):
        import json
        (Path(self.tmp.name)/'site_config.json').write_text(json.dumps({'download_url':'https://unrelated.example/other.apk'}))
        with patch.object(views,'ROOT',Path(self.tmp.name)):
            self.assertEqual(views.configuration()['download_url'],'/downloads/dokon-boshqaruv.apk')
    def test_all_languages_and_cookie_persistence(self):
        for code,title in [('uz','Imkoniyatlar'),('ru','Возможности'),('en','Features')]:
            for path in ['/','/download/','/missing/']:
                r=self.client.get(path,{'lang':code})
                self.assertContains(r,f'lang="{code}"',status_code=404 if path=='/missing/' else 200)
                self.assertContains(r,title,status_code=r.status_code)
                self.assertEqual(r.cookies['website_language'].value,code)
            r=self.client.get('/download/')
            self.assertContains(r,f'lang="{code}"')
        r=self.client.get('/',{'lang':'bad<script>'});self.assertContains(r,'lang="uz"')
    def test_catalog_complete(self):
        for key,value in CATALOG.items():
            self.assertEqual(set(value),{'uz','ru','en'},key)
            self.assertTrue(all(value.values()),key)
    def test_admin_contact_translations(self):
        from website.models import SiteSettings
        SiteSettings.objects.create(contact_title='Uzbek sarlavha',contact_title_ru='Русский заголовок',contact_text_en='Contact our team')
        self.assertContains(self.client.get('/',{'lang':'ru'}),'Русский заголовок')
        self.assertContains(self.client.get('/',{'lang':'en'}),'Contact our team')
        self.assertNotContains(self.client.get('/',{'lang':'en'}),'Uzbek sarlavha')
    def test_phones_receive_the_same_apk(self):
        url='/downloads/dokon-boshqaruv.apk'
        for agent in ['Mozilla/5.0 Android Chrome/130','Telegram Android','Instagram Android']:
            r=self.client.get(url,HTTP_USER_AGENT=agent)
            self.assertEqual(r.status_code,200)
            self.assertEqual(r['Content-Disposition'],'attachment; filename="e-dukon.apk"')
            self.assertEqual(self.body(r),self.payload)
