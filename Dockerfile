# استخدم صورة Python أساسية تحتوي على تبعيات WeasyPrint
FROM python:3.10-slim-buster

# تثبيت تبعيات النظام المطلوبة لـ WeasyPrint
# هذه الخطوة ضرورية جداً لمكتبة WeasyPrint
# تشمل المكتبات الأساسية لـ Cairo, Pango, GDK-Pixbuf, FFI
# بالإضافة إلى مكتبات الخطوط (fontconfig)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libjpeg-dev \
    zlib1g \
    libpangocairo-1.0-0 \
    libgirepository-1.0-1 \
    gobject-introspection \
    fontconfig \
    libharfbuzz-icu0 && \
    rm -rf /var/lib/apt/lists/*

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# نسخ ملف requirements.txt إلى دليل العمل
COPY requirements.txt .

# تثبيت تبعيات Python من requirements.txt
# هذا الأمر سيقوم بتثبيت Flask, Gunicorn, WeasyPrint
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى دليل العمل
# (مثل app.py، وقالب الـ HTML، وأي ملفات أخرى)
COPY . .

# أمر البدء الافتراضي لتشغيل التطبيق باستخدام Gunicorn
# يربط Gunicorn بالمنفذ 10000 الذي تستخدمه Render
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]