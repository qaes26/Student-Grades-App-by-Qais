from flask import Flask, render_template, request, send_file, redirect, url_for
from io import BytesIO
from weasyprint import HTML, CSS
import datetime # لإضافة التاريخ الحالي لتقرير PDF

app = Flask(__name__)

# قاموس لتخزين علامات الطلاب مع تفاصيل المواد
students_grades = {} # بنية البيانات: {'الطالب': {'المادة': العلامة, ...}, ...}

# دالة لحساب المعدل التراكمي للطالب
def calculate_gpa(student_name):
    if student_name not in students_grades or not students_grades[student_name]:
        return "لا توجد مواد"
    
    total_grades = sum(students_grades[student_name].values())
    num_subjects = len(students_grades[student_name])
    if num_subjects == 0: # تجنب القسمة على صفر إذا لم تكن هناك مواد
        return "لا توجد مواد" # أو يمكنك إرجاع 0.0 إذا كنت تفضل رقماً
    return round(total_grades / num_subjects, 2) # تقريب لرقمين عشريين

# دالة مساعدة لتجهيز بيانات الطلاب مع المعدل لتمريرها للقوالب
def get_students_data_for_template():
    students_with_gpa = {}
    for name, subjects in students_grades.items():
        students_with_gpa[name] = {
            'subjects': subjects,
            'gpa': calculate_gpa(name)
        }
    return students_with_gpa

@app.route('/')
def index():
    programmer_name = "قيس طلال الجازي"
    return render_template('index.html', 
                           programmer_name=programmer_name, 
                           all_students_data=get_students_data_for_template())

@app.route('/add_grade', methods=['POST'])
def add_grade():
    student_name = request.form['student_name'].strip()
    subject_name = request.form['subject_name'].strip()
    
    if not student_name or not subject_name:
        message = "الرجاء إدخال اسم الطالب واسم المادة."
        return render_template('index.html', 
                               programmer_name="قيس طلال الجازي", 
                               all_students_data=get_students_data_for_template(), 
                               message=message)

    try:
        grade = float(request.form['grade'])
        if 0 <= grade <= 100:
            if student_name not in students_grades:
                students_grades[student_name] = {}
            
            if subject_name in students_grades[student_name]:
                message = f"تم تحديث علامة الطالب {student_name} في مادة {subject_name} من {students_grades[student_name][subject_name]} إلى {grade} بنجاح!"
            else:
                message = f"تمت إضافة علامة {grade} للطالب {student_name} في مادة {subject_name} بنجاح!"

            students_grades[student_name][subject_name] = grade
            
        else:
            message = "الرجاء إدخال علامة بين 0 و 100."
    except ValueError:
        message = "إدخال غير صالح للعلامة. الرجاء إدخال رقم للعلامة."
    
    return render_template('index.html', 
                           programmer_name="قيس طلال الجازي", 
                           all_students_data=get_students_data_for_template(), 
                           message=message)

@app.route('/delete_grade/<student_name>/<subject_name>', methods=['POST'])
def delete_grade(student_name, subject_name):
    """
    حذف علامة مادة محددة لطالب معين.
    """
    message = "حدث خطأ أثناء الحذف."
    if student_name in students_grades:
        if subject_name in students_grades[student_name]:
            del students_grades[student_name][subject_name]
            message = f"تم حذف علامة {subject_name} للطالب {student_name} بنجاح."
            # إذا لم يعد للطالب أي مواد، احذف الطالب من القاموس
            if not students_grades[student_name]:
                del students_grades[student_name]
        else:
            message = f"المادة {subject_name} غير موجودة للطالب {student_name}."
    else:
        message = f"الطالب {student_name} غير موجود."
    
    return render_template('index.html', 
                           programmer_name="قيس طلال الجازي", 
                           all_students_data=get_students_data_for_template(), 
                           message=message)

@app.route('/edit_grade', methods=['POST'])
def edit_grade():
    """
    معالجة تعديل علامة مادة محددة لطالب معين.
    """
    student_name = request.form['edit_student_name'].strip()
    subject_name = request.form['edit_subject_name'].strip()
    
    message = "حدث خطأ أثناء التعديل."
    if student_name in students_grades and subject_name in students_grades[student_name]:
        try:
            new_grade = float(request.form['new_grade'])
            if 0 <= new_grade <= 100:
                students_grades[student_name][subject_name] = new_grade
                message = f"تم تعديل علامة {subject_name} للطالب {student_name} إلى {new_grade} بنجاح."
            else:
                message = "الرجاء إدخال علامة بين 0 و 100."
        except ValueError:
            message = "إدخال غير صالح للعلامة الجديدة. الرجاء إدخال رقم."
    else:
        message = "الطالب أو المادة غير موجودة للتعديل."
    
    return render_template('index.html', 
                           programmer_name="قيس طلال الجازي", 
                           all_students_data=get_students_data_for_template(), 
                           message=message)

@app.route('/export_grades_pdf')
def export_grades_pdf():
    """
    مسار لتوليد ملف PDF لعلامات الطلاب والمعدل التراكمي.
    """
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    html_content = render_template('pdf_template.html', 
                                   all_students_data=get_students_data_for_template(), 
                                   current_date=current_date)

    # Simplified CSS for PDF to reduce potential errors with WeasyPrint
    pdf_styles = CSS(string='''
        body { 
            font-family: 'Arial', sans-serif; 
            direction: rtl; 
            text-align: right; 
            margin: 30px; 
            font-size: 12px; 
            color: #333; 
            line-height: 1.5; 
        }
        h1 { 
            color: #0056b3; 
            text-align: center; 
            margin-bottom: 20px; 
            padding-bottom: 5px; 
            border-bottom: 1px solid #ccc; 
        }
        .student-section { 
            margin-bottom: 25px; 
            border: 1px solid #eee; 
            padding: 15px; 
            border-radius: 5px; 
            background-color: #fcfcfc; 
            page-break-inside: avoid; /* لمنع تقسيم قسم الطالب الواحد عبر الصفحات */
        }
        .student-name { 
            font-size: 1.3em; 
            color: #007bff; 
            margin-bottom: 8px; 
            font-weight: bold; 
            text-align: center; 
        }
        h3 { 
            color: #4CAF50; 
            margin-top: 10px; 
            margin-bottom: 5px; 
            font-size: 1.0em; 
            font-weight: bold; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 5px; 
            background-color: #fff; 
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: right; 
        }
        th { 
            background-color: #eaf6ff; 
            color: #0056b3; 
            font-weight: bold; 
        }
        .student-gpa { 
            font-size: 1.1em; 
            color: #28a745; 
            font-weight: bold; 
            margin-top: 15px; 
            text-align: center; 
            background-color: #e6ffe6; 
            padding: 8px; 
            border-radius: 4px; 
            border: 1px solid #c3e6cb; 
        }
        .no-data { 
            text-align: center; 
            color: #777; 
            margin-top: 10px; 
            font-style: italic; 
        }
        .footer { 
            margin-top: 40px; 
            text-align: center; 
            font-size: 0.8em; 
            color: #666; 
            border-top: 1px dashed #ccc; 
            padding-top: 10px; 
        }
        @page { size: A4; margin: 1.5cm; }
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