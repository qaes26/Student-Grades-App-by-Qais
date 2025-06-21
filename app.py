from flask import Flask, render_template, request

app = Flask(__name__)

# قاموس لتخزين أسماء الطلاب وعلاماتهم
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

if __name__ == '__main__':
    app.run(debug=True)