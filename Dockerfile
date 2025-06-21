# استخدم صورة Python أساسية تحتوي على تبعيات WeasyPrint
# هذه الصورة مبنية خصيصاً لتشمل Pango, Cairo, وغيرها
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
# هذا هو نفس الأمر الموجود في Procfile
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]