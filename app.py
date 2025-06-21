from flask import Flask, render_template, request, send_file
import io
from weasyprint import HTML, CSS # هذا السطر لاستخدام مكتبة WeasyPrint لتوليد PDF

app = Flask(__name__)

# قاموس لتخزين أسماء الطلاب وعلاماتهم
# **ملاحظة مهمة:** هذا القاموس يتم إعادة تعيينه في كل مرة يتم فيها إعادة تشغيل التطبيق (مثلاً عند التحديث على Render).
# في تطبيق حقيقي، ستحتاج إلى قاعدة بيانات (مثل SQLite أو PostgreSQL) لتخزين البيانات بشكل دائم.
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
    يولد ملف PDF يحتوي على علامات الطلاب فقط.
    """
    # نستخدم قالب HTML منفصل لهذا الغرض (grades_only_pdf.html)
    # لإعطاء تحكم كامل في مظهر الـ PDF
    html_string = render_template('grades_only_pdf.html', grades=students_grades)

    # يمكن إضافة بعض الـ CSS الأساسي لتحسين المظهر في الـ PDF
    # (هذا الـ CSS سيُطبق فقط على ملف الـ PDF)
    css_string = """
    @page { size: A4; margin: 2cm; } /* لإعدادات الصفحة والمسافات الهامشية */
    body {
        font-family: 'Arial', sans-serif;
        color: #333;
        direction: rtl; /* لدعم اللغة العربية */
        text-align: right;
        line-height: 1.6;
    }
    h1 {
        color: #0056b3;
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
    }
    ul {
        list-style: none;
        padding: 0;
        margin-top: 20px;
    }
    li {
        background-color: #f9f9f9; /* لون خلفية خفيف */
        margin-bottom: 12px;
        padding: 12px 20px;
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.1em;
        border: 1px solid #ddd; /* إطار خفيف */
    }
    span.name {
        font-weight: bold;
        color: #0056b3;
        flex-grow: 1; /* لتأخذ المساحة المتبقية */
        text-align: right;
        padding-left: 10px; /* مسافة بين الاسم والعلامة */
    }
    span.grade {
        background-color: #28a745;
        color: white;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
        min-width: 70px; /* لتنسيق موحد للعرض */
        text-align: center;
    }
    /* إذا لم تكن هناك علامات */
    p.no-grades {
        text-align: center;
        color: #777;
        font-size: 1.1em;
        padding: 20px;
        border: 1px dashed #ccc;
        border-radius: 8px;
        margin-top: 30px;
    }
    """

    # توليد ملف PDF باستخدام WeasyPrint
    html = HTML(string=html_string)
    pdf_bytes = html.write_pdf(stylesheets=[CSS(string=css_string)])

    # إرسال ملف PDF للمستخدم للتنزيل
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='علامات_الطلاب.pdf'
    )

# الجزء الخاص بالتشغيل المحلي (يمكن حذفه قبل الرفع لـ Render)
# Render يستخدم Gunicorn لتشغيل التطبيق مباشرة، فلا يحتاج لهذه الكتلة.
# إذا كنت لا تزال ترغب بتشغيل التطبيق محلياً للتجربة:
# if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=5000)