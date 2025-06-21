from flask import Flask, render_template, request, send_file
from io import BytesIO
from weasyprint import HTML, CSS # هذه المكتبات لميزة PDF

app = Flask(__name__)

# قاموس لتخزين أسماء الطلاب وعلاماتهم
# (هذا سيتم مسحه عند إعادة تشغيل التطبيق على Render، للتطبيقات الدائمة نحتاج قاعدة بيانات)
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
        message = "إدخال غير صالح للعلامة. الرجاء إدخال رقم للعلامة."
    
    programmer_name = "قيس طلال الجازي"
    return render_template('index.html', programmer_name=programmer_name, grades=students_grades, message=message)

@app.route('/export_grades_pdf')
def export_grades_pdf():
    """
    مسار لتوليد ملف PDF لعلامات الطلاب.
    """
    # إنشاء محتوى HTML لتقرير PDF
    # نمرر grades لـ pdf_template.html
    html_content = render_template('pdf_template.html', grades=students_grades)

    # تجهيز CSS أساسي للتصميم داخل الـ PDF
    # لاحظ: WeasyPrint بيدعم CSS، هذا مثال بسيط
    # يمكنك وضع CSS في ملف منفصل وربطه في pdf_template.html أيضاً
    pdf_styles = CSS(string='''
        body {
            font-family: 'Arial', sans-serif;
            direction: rtl;
            text-align: right;
            margin: 40px;
            font-size: 14px;
            color: #333;
        }
        h1 {
            color: #0056b3;
            text-align: center;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: right;
        }
        th {
            background-color: #f2f2f2;
            color: #0056b3;
            font-weight: bold;
        }
        .no-grades {
            text-align: center;
            color: #777;
            margin-top: 20px;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }
    ''')

    # تحويل HTML إلى PDF باستخدام WeasyPrint
    pdf_file = BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_file, stylesheets=[pdf_styles])
    pdf_file.seek(0) # ارجع لبداية الملف

    # إرسال ملف PDF للمستخدم
    return send_file(pdf_file,
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name='علامات_الطلاب.pdf')

# هذا الجزء لا يحتاجه Render عند النشر، ولكنه مفيد للتشغيل المحلي
# يمكنك حذفه قبل الرفع للإنتاج إذا أردت
if __name__ == '__main__':
    # تأكد أن Debug هو False في الإنتاج
    app.run(debug=True, host='0.0.0.0', port=5000)