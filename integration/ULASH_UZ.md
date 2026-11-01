# Mavjud backend bilan birga ishlatish

Mustaqil website deploy qilish eng sodda yo‘l. Agar website va API bitta Django deployda bo‘lsa:

1. website papkasini backend yoniga qo‘ying (Docker ichida /website).
2. integration/backend/config/website_integration.py ni backend/config/ ichiga nusxalang.
3. backend/config/settings.py OXIRIGA yozing:

```python
from config.website_integration import configure_website
configure_website(globals())
```

4. backend/config/urls.py OXIRIGA yozing:

```python
from config.website_integration import mount_website
urlpatterns = mount_website(urlpatterns)
```

5. python manage.py migrate bajaring. Mavjud backend admin akkaunti bilan /admin/ ga kiring. “e-dukon sayti → Sayt sozlamalari” mavjud bo‘ladi.

Eski config/urls.py ni to‘liq almashtirmang: inPAY va boshqa API yo‘llari saqlanishi kerak. Helper faqat aniq bosh sahifani websitega beradi; /api/ yo‘llariga tegmaydi. /website joylashuvini WEBSITE_ROOT bilan o‘zgartirish mumkin. Yangi fayllar backendning MEDIA_ROOT saqlash joyiga yoziladi; uni persistent volumega yo‘naltiring.
