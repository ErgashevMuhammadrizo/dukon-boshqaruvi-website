from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from urllib.parse import urlparse

class SiteSettings(models.Model):
    telegram_url = models.URLField('Telegram havolasi', blank=True, help_text='https://t.me/username')
    phone = models.CharField('Telefon', max_length=30, blank=True,
        validators=[RegexValidator(r'^[+0-9 ()-]{7,30}$', 'Telefon raqamini to‘g‘ri kiriting')])
    email = models.EmailField('Email / Gmail', blank=True)
    contact_title = models.CharField('Bog‘lanish sarlavhasi', max_length=160, default='Biznesingiz haqida gaplashamiz.')
    contact_text = models.TextField('Bog‘lanish matni', default='Savolingiz bormi? Sizga qulay kanalda yozing — e-dukon bilan ishlashni boshlashga yordam beramiz.')
    contact_title_ru = models.CharField('Ruscha aloqa sarlavhasi', max_length=160, blank=True)
    contact_text_ru = models.TextField('Ruscha aloqa matni', blank=True)
    contact_title_en = models.CharField('Inglizcha aloqa sarlavhasi', max_length=160, blank=True)
    contact_text_en = models.TextField('Inglizcha aloqa matni', blank=True)
    deals_url = models.URLField('DEALS rasmiy havolasi', blank=True, help_text='Ixtiyoriy: kompaniyangiz sayti yoki Telegram havolasi')
    windows_file = models.FileField('Windows o‘rnatuvchisi (.exe)', upload_to='releases/windows/', blank=True,
        validators=[FileExtensionValidator(['exe'])], help_text='To‘liq installer EXE yuklang. Faqat runner EXE barcha DLLsiz ishlamasligi mumkin.')
    windows_url = models.URLField('Windows tashqi yuklash havolasi', blank=True,
        help_text='Fayl yuklamasangiz, HTTPS orqali to‘g‘ridan-to‘g‘ri EXE havolasini kiriting.')
    windows_version = models.CharField('Windows versiyasi', max_length=40, blank=True)
    android_version = models.CharField('Android versiyasi', max_length=40, blank=True)
    updated_at = models.DateTimeField('Yangilangan', auto_now=True)
    class Meta:
        verbose_name = 'Sayt sozlamalari'
        verbose_name_plural = 'Sayt sozlamalari'
    def __str__(self): return 'e-dukon — kontaktlar va yuklamalar'
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    def clean(self):
        errors = {}
        for field in ['telegram_url', 'deals_url', 'windows_url']:
            value = getattr(self, field).strip()
            setattr(self, field, value)
            if value:
                parsed = urlparse(value)
                if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                    errors[field] = 'Faqat haqiqiy HTTPS havola kiriting'
        if self.telegram_url and urlparse(self.telegram_url).hostname not in ('t.me','telegram.me'):
            errors['telegram_url'] = 'https://t.me/username ko‘rinishida kiriting'
        if self.windows_url and not urlparse(self.windows_url).path.lower().endswith('.exe'):
            errors['windows_url'] = 'To‘g‘ridan-to‘g‘ri .exe fayl havolasini kiriting'
        if self.windows_file and not self.windows_file._committed:
            file = self.windows_file.file
            signature = file.read(2); file.seek(0)
            if signature != b'MZ': errors['windows_file'] = 'Bu Windows EXE fayli emas'
        if errors: raise ValidationError(errors)
