from django.test import TestCase, Client, override_settings
from website.domain import WEBSITE_HOST, WEBSITE_URL, configured_hosts, configured_origins, configured_site_url

class DomainTests(TestCase):
    def test_production_domain_is_accepted_without_env(self):
        self.assertIn(WEBSITE_HOST, configured_hosts({}))
        self.assertIn(WEBSITE_URL, configured_origins({}))
        self.assertEqual(configured_site_url({}), WEBSITE_URL)

    def test_existing_old_variables_do_not_remove_website_domain(self):
        hosts=configured_hosts({'ALLOWED_HOSTS':'old.example.test,https://other.example.test'})
        self.assertIn(WEBSITE_HOST,hosts);self.assertIn('other.example.test',hosts)

    def test_railway_domain_is_added_to_both_settings(self):
        env={'RAILWAY_PUBLIC_DOMAIN':'another.up.railway.app'}
        self.assertIn('another.up.railway.app',configured_hosts(env))
        self.assertIn('https://another.up.railway.app',configured_origins(env))
        self.assertNotIn('*',configured_hosts({'ALLOWED_HOSTS':'*'}))

    @override_settings(ALLOWED_HOSTS=[WEBSITE_HOST], SITE_URL=WEBSITE_URL,
        CSRF_TRUSTED_ORIGINS=[WEBSITE_URL],SESSION_COOKIE_SECURE=True,CSRF_COOKIE_SECURE=True)
    def test_real_host_pages_and_admin_csrf(self):
        client=Client(enforce_csrf_checks=True,HTTP_HOST=WEBSITE_HOST)
        for path in ['/', '/download/', '/admin/login/']:
            self.assertEqual(client.get(path,secure=True).status_code,200)
        page=client.get('/',secure=True)
        self.assertContains(page, 'rel="canonical" href="'+WEBSITE_URL+'/"')
        token=client.cookies['csrftoken'].value
        allowed=client.post('/admin/login/',{'username':'invalid','password':'invalid','csrfmiddlewaretoken':token},secure=True,HTTP_ORIGIN=WEBSITE_URL)
        self.assertEqual(allowed.status_code,200)
        denied=client.post('/admin/login/',{'csrfmiddlewaretoken':token},secure=True,HTTP_ORIGIN='https://attacker.example.test')
        self.assertEqual(denied.status_code,403)
