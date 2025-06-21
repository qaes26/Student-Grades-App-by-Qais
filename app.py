from flask import Flask, render_template, request, send_file
from io import BytesIO
from weasyprint import HTML, CSS
import datetime # لإضافة التاريخ الحالي لتقرير PDF

app = Flask(__name__)

# قاموس لتخزين علامات الطلاب مع تفاصيل المواد
# بنية جديدة: {'اسم الطالب': {'اسم المادة': العلامة, 'اسم المادة2': العلامة2, ...}, ...}
students_grades = {}

# دالة لحساب المعدل التراكمي للطالب
def calculate_gpa(student_name):
    if student_name not in students_grades or not students_grades[student_name]:
        return "لا توجد مواد"
    
    total_grades = sum(students_grades[student_name].values())
    num_subjects = len(students_grades[student_name])
    return round(total_grades / num_subjects, 2) # تقريب لرقمين عشريين

@app.route('/')
def index():
    """
    الصفحة الرئيسية لعرض النموذج ونتائج العلامات.
    """
    programmer_name = "قيس طلال الجازي"
    
    # نحسب المعدل لكل طالب قبل تمريره للقالب
    students_with_gpa = {}
    for name, subjects in students_grades.items():
        students_with_gpa[name] = {
            'subjects': subjects,
            'gpa': calculate_gpa(name)
        }

    return render_template('index.html', 
                           programmer_name=programmer_name, 
                           all_students_data=students_with_gpa) # تغيير اسم المتغير المرسل

@app.route('/add_grade', methods=['POST'])
def add_grade():
    """
    معالجة إضافة علامات الطلاب والمواد من النموذج.
    """
    student_name = request.form['student_name'].strip() # إزالة المسافات الزائدة
    subject_name = request.form['subject_name'].strip() # حقل جديد لاسم المادة
    
    if not student_name or not subject_name:
        message = "الرجاء إدخال اسم الطالب واسم المادة."
        programmer_name = "قيس طلال الجازي"
        students_with_gpa = {}
        for name, subjects in students_grades.items():
            students_with_gpa[name] = {
                'subjects': subjects,
                'gpa': calculate_gpa(name)
            }
        return render_template('index.html', 
                               programmer_name=programmer_name, 
                               all_students_data=students_with_gpa, 
                               message=message)

    try:
        grade = float(request.form['grade'])
        if 0 <= grade <= 100:
            if student_name not in students_grades:
                students_grades[student_name] = {} # إذا الطالب جديد، أنشئ قاموس للمواد
            students_grades[student_name][subject_name] = grade # إضافة المادة وعلامتها
            message = f"تمت إضافة علامة {grade} للطالب {student_name} في مادة {subject_name} بنجاح!"
        else:
            message = "الرجاء إدخال علامة بين 0 و 100."
    except ValueError:
        message = "إدخال غير صالح للعلامة. الرجاء إدخال رقم للعلامة."
    
    programmer_name = "قيس طلال الجازي"
    students_with_gpa = {}
    for name, subjects in students_grades.items():
        students_with_gpa[name] = {
            'subjects': subjects,
            'gpa': calculate_gpa(name)
        }
    return render_template('index.html', 
                           programmer_name=programmer_name, 
                           all_students_data=students_with_gpa, 
                           message=message)

@app.route('/export_grades_pdf')
def export_grades_pdf():
    """
    مسار لتوليد ملف PDF لعلامات الطلاب والمعدل التراكمي.
    """
    # نحسب المعدل لكل طالب قبل تمريره للقالب PDF
    students_with_gpa = {}
    for name, subjects in students_grades.items():
        students_with_gpa[name] = {
            'subjects': subjects,
            'gpa': calculate_gpa(name)
        }

    # إضافة التاريخ الحالي لتقرير PDF
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    html_content = render_template('pdf_template.html', 
                                   all_students_data=students_with_gpa, # تمرير البيانات المحدثة
                                   current_date=current_date)

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
        .student-section {
            margin-bottom: 30px;
            border: 1px solid #eee;
            padding: 15px;
            border-radius: 8px;
            background-color: #fcfcfc;
        }
        .student-name {
            font-size: 1.3em;
            color: #0056b3;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .student-gpa {
            font-size: 1.1em;
            color: #28a745;
            font-weight: bold;
            margin-top: 10px;
            text-align: center;
        }
    ''')

    pdf_file = BytesIO()
    # base_url مهمة لـ WeasyPrint عشان يتعرف على المسارات النسبية (إن وجدت)
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_file, stylesheets=[pdf_styles])
    pdf_file.seek(0)

    return send_file(pdf_file,
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'علامات_الطلاب_والمعدل_{current_date}.pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)