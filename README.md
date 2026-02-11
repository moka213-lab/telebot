# 🎓 بوت اصول الدين التعليمي

بوت تلغرام تعليمي متكامل مع لوحة تحكم احترافية، مصمم للاستضافة المجانية على Render وربطه مع بلوجر.

## المميزات

- ✅ بوت تلغرام متعدد السنوات الدراسية
- ✅ **لوحة تحكم احترافية** تتضمن:
  - 📊 نظرة عامة شاملة مع الإحصائيات
  - 📚 إدارة المحتوى التعليمي (إضافة/تعديل/حذف)
  - 👥 إدارة المستخدمين
  - 📢 الإرسال الجماعي مع جدولة
  - ⚙️ إعدادات البوت المتقدمة
  - 📋 سجلات مفصلة
- ✅ دعم التضمين في بلوجر
- ✅ جاهز للاستضافة على Render المجانية
- ✅ إحصائيات شاملة
- ✅ تصميم متجاوب يدعم جميع الأجهزة

## المتطلبات

- Python 3.9+
- حساب تلغرام (لبوت BotFather)
- حساب Render (للاستضافة المجانية)

## التثبيت المحلي

```bash
# استنساخ المشروع
git clone https://github.com/yourusername/telegram-bot-UsulAlDin.git
cd telegram-bot-UsulAlDin

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ ملف البيئة
cp .env.example .env

# تعديل المتغيرات في ملف .env
```

## إعداد متغيرات البيئة

عدّل ملف `.env` واضبط القيم التالية:

```env
TELEGRAM_TOKEN=your_bot_token_from_botfather
ADMIN_PASSWORD=your_secure_password
WEBHOOK_URL=https://your-app.onrender.com
SECRET_KEY=generate_random_string_here
PORT=8080
```

## إنشاء البوت على تلغرام

1. افتح BotFather: [@BotFather](https://t.me/BotFather)
2. أنشئ بوت جديد: `/newbot`
3. احصل على رمز الوصول (Token)
4. اضبط الويب هوك للبوت

## التشغيل المحلي

```bash
python main.py
```

## النشر على Render

### الخطوة 1: رفع الكود إلى GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/telegram-bot-UsulAlDin.git
git push -u origin main
```

### الخطوة 2: إنشاء خدمة على Render

1. سجّل الدخول إلى [Render Dashboard](https://dashboard.render.com)
2. انقر على **New +** واختر **Web Service**
3. اختر مستودع GitHub الخاص بك
4. اضبط الإعدادات:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.web:app --bind 0.0.0.0:$PORT --workers 1`

### الخطوة 3: إضافة متغيرات البيئة

في إعدادات الخدمة على Render، أضف:
- `TELEGRAM_TOKEN`: رمز البوت
- `ADMIN_PASSWORD`: كلمة مرور لوحة التحكم
- `WEBHOOK_URL`: رابط الخدمة (يُملأ تلقائياً بعد النشر)
- `SECRET_KEY`: مفتاح سري عشوائي

### الخطوة 4: ربط الويب هوك

بعد النشر، شغّل الأمر التالي (استبدل YOUR_URL و YOUR_TOKEN):

```bash
curl -F "url=YOUR_URL/webhook" https://api.telegram.org/botYOUR_TOKEN/setWebhook
```

## الوصول إلى لوحة التحكم

1. افتح الرابط: `https://your-app.onrender.com/login`
2. سجّل الدخول بكلمة المرور
3. ستظهر لوحة التحكم

## التضمين في بلوجر

لإضافة لوحة التحكم إلى بلوجر، استخدم الكود التالي:

```html
<iframe src="https://your-app.onrender.com/embed" width="100%" height="800" frameborder="0"></iframe>
```

## هيكل المشروع

```
telegram-bot-UsulAlDin/
├── app/
│   ├── __init__.py
│   ├── bot.py          # معالجة أوامر البوت
│   └── web.py          # خوادم الويب ولوحة التحكم
├── config.py           # إعدادات البيئة
├── main.py             # نقطة البداية
├── requirements.txt    # المتطلبات
├── Procfile            # إعداد Render
├── .env.example        # قالب المتغيرات
├── .gitignore          # تجاهل الملفات
└── README.md           # التوثيق
```

## المسارات

| المسار | الوصف |
|--------|-------|
| `/` | توجيه إلى لوحة التحكم |
| `/login` | صفحة تسجيل الدخول |
| `/dashboard` | لوحة التحكم الرئيسية |
| `/embed` | نسخة مبسطة للتضمين |
| `/broadcast` | إرسال رسالة جماعية |
| `/settings` | تحديث إعدادات البوت |
| `/content/add` | إضافة محتوى جديد |
| `/webhook` | نقطة استقبال تحديثات تلغرام |
| `/health` | فحص حالة الخدمة |
| `/api/stats` | إحصائيات بصيغة JSON |

## استكشاف الأخطاء

### البوت لا يستجيب
- تحقق من تسجيل الدخول إلى Render
- تأكد من صحة TELEGRAM_TOKEN
- راجع سجلات Render

### لا يمكن تسجيل الدخول
- تحقق من ADMIN_PASSWORD
- تأكد من SECRET_KEY

### الويب هوك لا يعمل
- تأكد من إعداد الويب هوك بشكل صحيح
- راجع سجلات التطبيق

## المساهمة

نرحب بطلبات السحب والإصلاحات!

## الترخيص

MIT License - استخدمه بحرية

---

**صُنع بـ ❤️ للمجتمع التعليمي**
