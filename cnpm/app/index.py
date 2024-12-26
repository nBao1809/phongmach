from datetime import date

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from app import app, dao, login
import admin


@app.route('/')
def index():
    return render_template('index.html')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)

            next = request.args.get('next')
            return redirect(next if next else '/')

    return render_template('login.html')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route("/datLich")
def datLich():
    today = date.today()
    return render_template('datlich.html', today=today)


patients_data = [
    {"id": 1, "full_name": "Nguyen Van A", "birth_date": "1985-01-01", "phone": "0901234567", "address": "Hà Nội",
     "gender": "Nam", "date": "2024-12-26", "confirmed": False},
    {"id": 2, "full_name": "Tran Thi B", "birth_date": "1990-02-15", "phone": "0912345678",
     "address": "TP. Hồ Chí Minh", "gender": "Nữ", "date": "2024-12-26", "confirmed": False},
    {"id": 3, "full_name": "Le Van C", "birth_date": "1988-05-10", "phone": "0934567890", "address": "Đà Nẵng",
     "gender": "Nam", "date": "2024-12-27", "confirmed": False}
]


@app.route("/quanlydanhsachkham")
def quanlydanhsachkham():
    available_dates = sorted(set(patient['date'] for patient in patients_data if not patient['confirmed']))
    return render_template('quanlydanhsachkham.html', patients=[],available_dates=available_dates)


@app.route("/quanlyphieukham")
def quanlyphieukham():
    return  render_template('quanlyphieukham.html')



# API lấy danh sách bệnh nhân theo ngày
@app.route('/api/patients')
def get_patients():
    date = request.args.get('date')
    filtered_patients = [p for p in patients_data if p['date'] == date and not p['confirmed']]
    return jsonify({"patients": filtered_patients})


# API xóa bệnh nhân
@app.route('/api/patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    global patients_data
    patients_data = [p for p in patients_data if p['id'] != patient_id]
    return jsonify({"message": "Deleted successfully"}), 200

@app.route('/api/confirm-day', methods=['POST'])
def confirm_day():
    date = request.args.get('date')
    for patient in patients_data:
        if patient['date'] == date:
            patient['confirmed'] = True
    return jsonify({"message": "All patients confirmed for the day"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)
