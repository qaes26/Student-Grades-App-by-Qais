# استخدم صورة Python أساسية تحتوي على تبعيات WeasyPrint
FROM python:3.10-slim-buster

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# نسخ ملف requirements.txt إلى دليل العمل
COPY requirements.txt .

# تثبيت تبعيات Python
# هذا الأمر سيقوم بتثبيت Flask, Gunicorn, WeasyPrint
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى دليل العمل
COPY . .
# أمر البدء الافتراضي لتشغيل التطبيق باستخدام Gunicorn
# يستخدم المنفذ 10000 مباشرة، وهو المنفذ الافتراضي الذي توفره Render
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]