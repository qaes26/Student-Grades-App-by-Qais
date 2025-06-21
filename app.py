from flask import Flask, render_template, request, send_file
from io import BytesIO
from weasyprint import HTML, CSS
from datetime import datetime # لإضافة التاريخ في تقرير الـ PDF

app = Flask(__name__)

# قاموس لتخزين أسماء الطلاب وعلاماتهم
# هذا القاموس سيعاد تعيينه كلما أعيد تشغيل التطبيق على Render
# للحفاظ على البيانات بشكل دائم، ستحتاج إلى قاعدة بيانات (وهذا موضوع آخر)
students_grades = {}

@app.route('/')
def index():
    """
    الصفحة الرئيسية لعرض النموذج ونتائج العلامات.
    """
    programmer_name = "قيس طلال الجازي"
    return render_template('index.html', programmer_name=programmer_name, grades=students_grades)

@app.route('/add_grade', methods=['POST'])
def add_grade():
    """
    معالجة إضافة علامات الطلاب من النموذج.
    """
    student_name = request.form['student_name']
    try:
        grade = float(request.form['grade'])
        if 0 <= grade <= 100:
            students_grades[student_name] = grade
            message = "تمت إضافة العلامة بنجاح!"
        else:
            message = "الرجاء إدخال علامة بين 0 و 100."
    except ValueError:
        message = "إدخال غير صالح للعلامة. الرجاء إدخال رقم."
    
    programmer_name = "قيس طلال الجازي"
    return render_template('index.html', programmer_name=programmer_name, grades=students_grades, message=message)

@app.route('/export_grades_pdf')
def export_grades_pdf():
    """
    معالجة طلب تصدير علامات الطلاب إلى ملف PDF.
    """
    # الحصول على التاريخ الحالي لإدراجه في التقرير
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # إنشاء محتوى HTML لتقرير PDF باستخدام قالب منفصل
    # نمرر له العلامات والتاريخ الحالي
    html_content = render_template('pdf_template.html', grades=students_grades, current_date=current_date)

    # تحويل HTML إلى PDF باستخدام WeasyPrint
    pdf_file = BytesIO()
    # base_url=request.base_url ضرورية لـ WeasyPrint للتعامل مع المسارات النسبية (إذا كان لديك صور أو ملفات CSS خارجية)
    # stylesheets=[CSS(string='...')] هنا نضيف CSS أساسي لضمان دعم اللغة العربية بشكل جيد.
    HTML(string=html_content, base_url=request.base_url).write_pdf(
        pdf_file,
        stylesheets=[CSS(string='body { font-family: Arial, sans-serif; direction: rtl; text-align: right; }')]
    )
    pdf_file.seek(0) # ارجع لبداية الملف عشان send_file تقرأه من البداية

    # إرسال ملف PDF للمستخدم للتحميل
    return send_file(pdf_file,
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'علامات_الطلاب_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf')

# هذا الجزء فقط للتشغيل المحلي، ولن يتم استخدامه على Render (حيث يستخدم Gunicorn)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)