# Railway domeni kodga biriktirildi

Sayt domeni: https://dukon-boshqaruvi-website-production.up.railway.app/
Admin: https://dukon-boshqaruvi-website-production.up.railway.app/admin/

Domen settings orqali ALLOWED_HOSTS va CSRF_TRUSTED_ORIGINS ga avtomatik qo‘shiladi. SITE_URL, canonical va Open Graph havolalari ham shu website domeniga moslandi. Railway’ning boshqa domeni bo‘lsa RAILWAY_PUBLIC_DOMAIN orqali ham qabul qilinadi. Ilova backend API yoki inPAY callback domeni almashtirilmadi.

Deploy: ushbu website kodini Railway’dagi WEBSITE servisiga yuklang va redeploy qiling. Bu ZIP tayyorlangan; Railway servisiga ushbu suhbatdan deploy qilinmagan. DJANGO_SECRET_KEY avvalgi doimiy qiymat bo‘lib qolsin. DATA_ROOT=/data uchun persistent volume saqlansin. Docker ishga tushganda migratsiyalarni bajaradi.

# e-dukon website · DEALS

Mahsulot sayti, admin paneldan boshqariladigan kontaktlar va Android/Windows yuklamalari.

## Birinchi ishga tushirish

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Avval .env.example dan .env yarating. Lokal sinov uchun DEBUG=1 va DATA_ROOT=var yozing. Ishlab chiqarish uchun DEBUG=0, kamida 50 belgili doimiy DJANGO_SECRET_KEY, ALLOWED_HOSTS va CSRF_TRUSTED_ORIGINS kiriting. Tasodifiy kalit yaratish: `python -c "import secrets; print(secrets.token_urlsafe(64))"`. Secretni chat yoki GitHubga joylamang.

## Admin panel

/admin/ ga createsuperuser orqali yaratgan akkauntingiz bilan kiring. “e-dukon sayti → Sayt sozlamalari → Qo‘shish” ni oching. Bitta umumiy sozlama yozuvi mavjud bo‘ladi; keyingi safar uni tahrirlang.

- Telegram: https://t.me/username
- Telefon: +998 90 123 45 67
- Email: sizning Gmail yoki boshqa emailingiz
- Kontakt sarlavhasi va tavsifi
- DEALS rasmiy sayti/Telegrami — ixtiyoriy; kiritilsa kompaniya blokida havola chiqadi
- Windows: to‘liq installer .exe faylini yuklang YOKI HTTPS EXE havolasini kiriting
- Android va Windows versiya belgilarini kiriting

Saqlagach ochiq saytni yangilang. Kontaktlar dizayndagi alohida kartalarda chiqadi. Bo‘sh kanal yashiriladi. EXE yo‘q bo‘lsa “Windows versiyasi tayyorlanmoqda” chiqadi; fayl yuklangach tugma avtomatik faollashadi. Sayt EXE yaratmaydi: tayyor installer yuklanadi. Oddiy Flutter runner EXE DLL/data fayllarisiz mustaqil ishlamasligi mumkin.

## Railway

Ushbu website papkasini alohida servisga deploy qilish mumkin. Dockerfile mavjud. Variables:

```env
DJANGO_SECRET_KEY=haqiqiy-tasodifiy-uzun-doimiy-kalit
DEBUG=0
ALLOWED_HOSTS=dukon-boshqaruvi-website-production.up.railway.app
CSRF_TRUSTED_ORIGINS=https://dukon-boshqaruvi-website-production.up.railway.app
DATA_ROOT=/data
```

Persistent volume ni /data ga ulang: admin kontaktlari va yuklangan fayllar restartdan keyin saqlanishi uchun zarur. Mavjud ma’lumotli volume va kalitlarni almashtirmang. Docker start migrate ni avtomatik bajaradi; birinchi adminni Railway shell ichida `python /app/website/manage.py createsuperuser` bilan yarating. Windows fayllari /data/media, baza /data/website.sqlite3 ichida bo‘ladi. Muntazam backup qiling.

Mavjud backend bilan birga joylashtirish uchun integration/ULASH_UZ.md ni o‘qing. Backend config/urls.py ni to‘liq almashtirish kerak emas — inPAY API yo‘llari saqlanadi.

## Yuklamalar

Siz yuborgan original APK `public/downloads/dokon-boshqaruv.apk` ichida saqlandi; ushbu ishda qayta yig‘ilmadi. URL ham saqlandi. Yangi APKni shu fayl o‘rniga qo‘ying. Windows uchun /downloads/e-dukon-setup.exe yo‘li admin yuklagan o‘rnatuvchini beradi. Yangi nom fayl yoki buildning ichki brendini o‘zgartirmaydi.

## Tekshiruv

16 ta Django testi va 8 ta JavaScript testi o‘tdi. Admin kontakt saqlashi, ochiq saytga chiqishi, login himoyasi, havola validatsiyasi, HTML escape, EXE GET/HEAD va mavjud bo‘lmagan fayl holati tekshirildi. Brauzerda render qilingan bosh sahifa, aloqa kartalari va yuklash sahifasi ko‘rildi. Haqiqiy hosting deploy va Windows o‘rnatuvchisining ishlashi ushbu ishda sinovdan o‘tkazilmadi. Test uchun ko‘rsatilgan demo kontaktlar, lokal baza va shaxsiy .env arxivga kiritilmagan.
