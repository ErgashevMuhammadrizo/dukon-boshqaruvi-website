# Yuklamalar va uch til yangilanishi

## Railway’da o‘rnatish

ZIP ichidagi `website/` — servisning loyiha ildizi. Railway shu papkadagi Dockerfile bilan yig‘ilsin.
Mavjud Railway Variables, ma’lumotlar bazasi va /data volume saqlansin. ZIP ichida haqiqiy .env yo‘q.
Docker ishga tushganda yangi migratsiya avtomatik qo‘llanadi; qo‘lda start qilsangiz `python manage.py migrate --noinput` bajaring.

Domeningiz Target Port 8081 bo‘lsa, Variables ichida `PORT=8081` bo‘lsin. So‘ng Redeploy qiling.
`DJANGO_SECRET_KEY` mavjud doimiy maxfiy kalit bo‘lib qoladi (kamida 50 belgi); .env.example dagi namunani haqiqiy kalit o‘rniga qo‘ymang.

## Nima tuzatildi

- APK havolasi faqat saytning `/downloads/dokon-boshqaruv.apk` manziliga bog‘langan. Eski site_config.json dagi boshqa domen/APK havolasi endi ishlatilmaydi.
- Fayl brauzerga `e-dukon.apk` nomi, Android MIME turi va aniq hajmi bilan yuboriladi.
- `Accept-Ranges`, `206 Partial Content`, `Content-Range`, ETag va If-Range qo‘shildi. Mos brauzer uzilgan yuklamani davom ettirishi mumkin; fayl almashtirilgan bo‘lsa eski-yangi bo‘laklar aralashtirilmaydi.
- Fayl oqimda uzatiladi, butun 82 MB fayl server xotirasiga yuklanmaydi. Gunicorn threadlari va 300 soniyali timeout qo‘shildi.
- UZ / RU / EN tanlash bosh sahifa, yuklash, 404, namuna interfeys, meta va yuklash xabarlariga tatbiq etildi. Tanlov cookie orqali eslab qolinadi. JavaScript o‘chirilganda ham tillar va to‘g‘ridan-to‘g‘ri yuklash ishlaydi.
- Admin → Sayt sozlamalari → Aloqa tarjimalari orqali ruscha/inglizcha sarlavha va matnlarni kiriting. Bo‘sh qolsa shu tilning standart matni chiqadi. Raqam, Telegram va email umumiy.

## “Boshqa dastur” haqidagi topilma

Arxivdagi APK ichida `Dokon Boshqaruv` nomi va `com.example.dokon_boshqaruv` paket identifikatori bor. ZIP tekshiruvida buzilgan element topilmadi, Android manifest va Flutter kutubxonasi mavjud.
Bu eski yig‘ilma o‘z holicha saqlandi. Sayt faylini qayta nomlash ilova ichidagi nom/ikonkani o‘zgartirmaydi. Ichki nomni e-dukon qilish uchun Flutter ilovasini mos signing kaliti bilan qayta yig‘ib, APKni `public/downloads/dokon-boshqaruv.apk` o‘rniga qo‘yish kerak. APK tahrirlanmadi yoki qayta imzolanmadi.
Foydalanuvchi telefonida aynan boshqa dastur o‘rnatilgan bo‘lsa, uning nomi/paketini bilmasdan sababni qat’iy aytib bo‘lmaydi.

## Telefonlarda tekshirish

1. Redeploy tugagach eski yuklamani bir marta o‘chirib, yangi havolani tashqi Chrome brauzerida oching.
2. Android yuklash tugmasini bosing. Fayl nomi e-dukon.apk bo‘lishi kerak.
3. Aloqani vaqtincha uzing va brauzer Yuklamalar bo‘limidagi Davom ettirishni bosing. Davom ettirishni brauzerning o‘zi qo‘llashi kerak.
4. Telegram/Instagram ichki brauzerida muammo bo‘lsa, tashqi brauzerda oching. iPhone Android APK o‘rnatmaydi.
5. UZ/RU/EN ni almashtiring, yuklash sahifasiga o‘ting, tanlangan til saqlanganini tekshiring.

Mahalliy testlar uzilgan faylni bo‘laklardan aynan qayta yig‘ishni tekshiradi. Haqiqiy Railway proksi cheklovlari, telefon xotirasi va brauzerning resume xatti-harakati bu ZIP orqali kafolatlanmaydi; redeploydan keyin yuqoridagi sinov zarur.
