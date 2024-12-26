import hashlib
from datetime import date, datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from app import app, dao, login, db
import admin
from app.models import UserEnum, Regulation, User, Appointment_list, Patient_Appointment, Patient


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


@app.route("/datlich")
def datlich():
    today = date.today()
    max = int(datetime.now().year)
    return render_template('datlich.html', today=today, max=max)


# dat lich
@app.route("/datlich/<string:phone>")
def get_patient_by_phone_api(phone):
    patient = dao.get_patient_by_phone(phone)
    if patient:
        return jsonify(patient.toDict())
    else:
        return jsonify(error="patient not found"), 404


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password, role=UserEnum.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')


@app.route("/api/datlich", methods=['POST'])
def api_datlich():
    date = request.get_json().get('date')  # Lấy ngày từ JSON
    patient_id = request.get_json().get('patient_id')
    limit_record = Regulation.query.filter(Regulation.name == "Giới hạn bệnh nhân").first()

    if limit_record:
        limit = limit_record.regulation
    else:
        return jsonify(error="Không tìm thấy quy định"), 404  # Trả về lỗi nếu không tìm thấy quy định

    # Lấy cuộc hẹn cho ngày đã cho
    appointment = Appointment_list.query.filter(Appointment_list.date == date).first()

    if appointment:
        # Lấy danh sách bệnh nhân đã đặt cuộc hẹn cho cuộc hẹn này
        appointment_patients = Patient_Appointment.query.filter(
            Patient_Appointment.appointment_id == appointment.id).all()

        if len(appointment_patients) < limit:
            ma = dao.make_appointment(appointment=appointment, patient_id=patient_id)  # Tạo cuộc hẹn mới
            return jsonify(ma)
        else:
            return jsonify(error="Không còn trống lịch"), 403
    else:
        # Nếu không có cuộc hẹn nào, thêm một cuộc hẹn mới
        a = dao.add_appointment_list(date)  # Giả sử bạn cần truyền ngày vào hàm này
        ma = dao.make_appointment(appointment=appointment, patient_id=patient_id)  # Tạo cuộc hẹn mới
    return jsonify(ma)


if __name__ == '__main__':
    app.run(debug=True, port=5001)


@app.before_first_request
def before_first_request():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            u = User(name='admin', username='admin', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
                     user_role=UserEnum.ADMIN)
        db.session.add(u)
        db.session.commit()
        if not Regulation.query.first():
            r = Regulation(name="Giới hạn bệnh nhân", regulation=40)
        r2 = Regulation(name="Tiền khám", regulation=100000)
        db.session.add(r)
        db.session.add(r2)
        db.session.commit()
