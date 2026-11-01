from pathlib import Path
from tempfile import TemporaryDirectory
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from website.models import SiteSettings

@override_settings(ALLOWED_HOSTS=['testserver'],DEBUG=False)
class ContactAdminTests(TestCase):
    def test_admin_requires_login(self):
        response=self.client.get('/admin/website/sitesettings/add/')
        self.assertEqual(response.status_code,302)
        self.assertIn('/admin/login/',response.url)

    def test_admin_saves_contacts_which_appear_as_clickable_cards(self):
        user=get_user_model().objects.create_superuser(username='owner',email='owner@example.test',password='fixture-only-password')
        self.client.force_login(user)
        response=self.client.post('/admin/website/sitesettings/add/',{
            'telegram_url':'https://t.me/example_demo','phone':'+998 90 000 00 00',
            'email':'hello@example.test','contact_title':'Biz bilan bog‘laning',
            'contact_text':'Sizga yordam beramiz.','deals_url':'https://example.test/company',
            'windows_url':'','windows_version':'','android_version':'','_save':'Saqlash'})
        self.assertEqual(response.status_code,302,response.content[:400])
        self.assertEqual(SiteSettings.objects.count(),1)
        self.client.logout()
        page=self.client.get('/')
        self.assertContains(page,'href="https://t.me/example_demo"')
        self.assertContains(page,'href="tel:+998900000000"')
        self.assertContains(page,'href="mailto:hello@example.test"')
        self.assertContains(page,'class="contact-card')
        self.assertContains(page,'href="https://example.test/company"')

    def test_missing_windows_file_is_not_advertised_as_ready(self):
        page=self.client.get('/download/')
        self.assertContains(page,'Windows versiyasi tayyorlanmoqda')
        self.assertEqual(self.client.get('/downloads/e-dukon-setup.exe').status_code,404)

    def test_windows_upload_streams_file_and_head_without_public_media_listing(self):
        with TemporaryDirectory() as root, override_settings(MEDIA_ROOT=root):
            # Route-only synthetic fixture; not an actual installer.
            upload=SimpleUploadedFile('setup.exe',b'MZ'+b'fixture-only',content_type='application/octet-stream')
            settings=SiteSettings(windows_file=upload,windows_version='1.0');settings.full_clean();settings.save()
            self.assertContains(self.client.get('/download/'),'Windows uchun yuklab olish (.exe)')
            response=self.client.get('/downloads/e-dukon-setup.exe')
            self.assertEqual(response.status_code,200)
            self.assertIn('e-dukon-setup.exe',response['Content-Disposition'])
            self.assertEqual(b''.join(response.streaming_content),b'MZfixture-only');response.close()
            head=self.client.head('/downloads/e-dukon-setup.exe')
            self.assertEqual(head.status_code,200);self.assertEqual(int(head['Content-Length']),14);head.close()

    def test_invalid_upload_and_unsafe_links_are_rejected(self):
        for values in [
            {'telegram_url':'https://fake.invalid/user'},
            {'windows_url':'javascript:alert(1)'},
            {'windows_url':'https://example.test/page.html'},
            {'deals_url':'https://user:pass@example.test/'},
            {'windows_file':SimpleUploadedFile('fake.exe',b'<html>')},
        ]:
            with self.assertRaises(ValidationError): SiteSettings(**values).full_clean()

    def test_public_custom_text_is_escaped(self):
        SiteSettings.objects.create(contact_title='<script>alert(1)</script>')
        response=self.client.get('/')
        self.assertNotContains(response,'<script>alert(1)</script>')
        self.assertContains(response,'&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_admin_styles_are_available(self):
        response=self.client.get('/static/admin/css/base.css')
        self.assertEqual(response.status_code,200);response.close()
