import hashlib
from datetime import date, datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from sendSMS import sendSMS
from app import app, dao, login, db
import admin
from app.models import UserEnum, Regulation, User, Appointment_list, Patient_Appointment, Patient, GenderEnum, Bill


@app.route('/')
def index():
    return render_template('index.html')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/login', methods=['get', 'post'])
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


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/datlich')
def datlich():
    today = date.today()
    return render_template('datlich.html', today=today)


@app.route('/quanlydanhsachkham')
def quanlydanhsachkham():
    available_dates = dao.get_date()
    return render_template('quanlydanhsachkham.html', available_dates=available_dates)


@app.route('/quanlyphieukham')
def quanlyphieukham():
    return render_template('quanlyphieukham.html')


@app.route('/thanhtoan')
def thanhtoan():
    return render_template('thanhtoan.html')


# API lấy danh sách bệnh nhân theo ngày
@app.route('/api/patients', methods=['GET', 'POST'])
def get_patients():
    date = request.args.get('date')
    appointment = Appointment_list.query.filter_by(date=date).first()
    patients = dao.get_all_patients(appointment)
    return jsonify({'appointment_id': appointment.id, 'patients': patients})


# API xóa bệnh nhân
@app.route('/api/patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    result = dao.delete_patient_in_appointment(patient_id=patient_id, appointment_id=appointment_id)
    if 'error' in result:
        return jsonify(result)
    else:
        return jsonify(result)


@app.route('/api/confirm-day', methods=['POST'])
def confirm_day():
    date = request.args.get('date')
    isConfirm = dao.confirm_appointment(date)
    appointment = Appointment_list.query.filter_by(date=date).first()
    patients = dao.get_all_patients(appointment)
    error_msg = []
    for patient in patients:
        msg = f"Kính gửi Quý khách {patient['name']}, lịch hẹn của bạn vào ngày {appointment.date}. Vui lòng đến đúng lịch. Cảm ơn!"
        # result=sendSMS(message=msg, number=patient.sdt)
        # if result.get('error'):
        #     error_msg.append({
        #         'patient_name': patient.name,
        #         'number': patient.sdt,
        #         'error': result['error']
        #     })
        # return jsonify({'appointment_id': appointment.id, 'patients': error_msg})
    return jsonify(isConfirm)


# dat lich
@app.route('/api/datlich/<string:phone>')
def get_patient_by_phone(phone):
    patient = dao.get_patient_by_phone(phone)
    if patient:
        return jsonify(patient.toDict())
    else:
        return jsonify(error='Không tìm thấy bệnh nhân'), 404


@app.route('/login-admin', methods=['POST'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password, role=UserEnum.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')


@app.route('/api/datlich', methods=['POST'])
def api_datlich():
    date = request.get_json().get('date')  # Lấy ngày từ JSON
    patient_id = int(request.get_json().get('patient_id'))
    limit_record = Regulation.query.filter(Regulation.name == 'Giới hạn bệnh nhân').first()
    if limit_record:
        limit = limit_record.regulation
    else:
        return jsonify(error='Không tìm thấy quy định'), 404  # Trả về lỗi nếu không tìm thấy quy định

    # Lấy cuộc hẹn cho ngày đã cho
    appointment = Appointment_list.query.filter(Appointment_list.date == date).first()
    if appointment:
        # Lấy danh sách bệnh nhân đã đặt cuộc hẹn cho cuộc hẹn này
        appointment_patients = Patient_Appointment.query.filter(
            Patient_Appointment.appointment_id == appointment.id).all()
        # Kiểm tra xem bệnh nhân đã đặt lịch chưa
        if any(ap.patient_id == patient_id for ap in appointment_patients):
            return jsonify(error='Người này đã đặt lịch rồi'), 403
        if len(appointment_patients) < limit:
            ma = dao.make_appointment(appointment=appointment, patient_id=patient_id)  # Tạo cuộc hẹn mới
            return jsonify(success='Đặt lịch thành công', appointment=ma), 200
        else:
            return jsonify(error='ngày này đã đủ bệnh nhân'), 403
    else:
        # Nếu không có cuộc hẹn nào, thêm một cuộc hẹn mới
        a = dao.add_appointment_list(date)
        ma = dao.make_appointment(appointment=a, patient_id=patient_id)  # Tạo cuộc hẹn mới
    return jsonify(success='Đặt lịch thành công', appointment=ma), 200


@app.route('/api/add_patient', methods=['POST'])
def add_patient():
    data = request.get_json()  # Nhận dữ liệu JSON từ yêu cầu

    # Lấy thông tin bệnh nhân từ dữ liệu
    name = data.get('name')
    phone = data.get('phone')
    birth_year = data.get('birthYear')
    gender = data.get('gender')
    if (gender == 'nam'):
        genderValue = 'MALE'
    else:
        genderValue = 'FEMALE'
    # Tạo đối tượng Patient
    new_patient = Patient(name=name, gender=GenderEnum[genderValue], birthday=birth_year, sdt=phone)

    isPatientExits = Patient.query.filter(Patient.sdt == new_patient.sdt).count() > 0
    if isPatientExits:
        return jsonify(error='bệnh nhân đã tồn tại'), 409
    # Thêm vào cơ sở dữ liệu
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'Bệnh nhân đã được thêm thành công!', 'id': new_patient.id}), 201


@app.route('/api/patient/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.get_json()
    id = patient_id
    name = data.get('name')
    birthday = data.get('birthday')
    sdt = data.get('sdt')
    gender = data.get('gender')
    if (gender == 'nam'):
        genderValue = 'MALE'
    else:
        genderValue = 'FEMALE'
    result = dao.update_patient(id=id, name=name, birthday=birthday, gender=GenderEnum[genderValue], sdt=sdt)
    return jsonify(result)


@app.route('/api/get_bill')
def get_all_bill():
    bill=dao.get_bill()
    return jsonify(bill)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)
        if not User.query.first():
            u = User(name='a', username='a', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
                     user_role=UserEnum.ADMIN)
            db.session.add(u)
            db.session.commit()
        if not Regulation.query.first():
            r = Regulation(name='Giới hạn bệnh nhân', regulation=40)
            r2 = Regulation(name='Tiền khám', regulation=100000)
            db.session.add(r)
            db.session.add(r2)
            db.session.commit()
