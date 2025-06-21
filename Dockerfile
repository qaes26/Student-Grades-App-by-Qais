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
# يستخدم متغير البيئة PORT الذي يحدده Render
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]