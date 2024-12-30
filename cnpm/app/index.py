import hashlib
from datetime import date, datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from pyexpat.errors import messages

from app import app, dao, login, db
import admin
from app.models import UserEnum, Regulation, User, Appointment_list, Patient_Appointment, Patient, GenderEnum, \
    Medication_consultation, Consultation_form, Medication, Medication_units, Bill


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
    available_dates = dao.get_date_status_1()
    return render_template('quanlyphieukham.html', available_dates=available_dates)


@app.route('/thanhtoan')
def thanhtoan():
    return render_template('thanhtoan.html')


# API lấy danh sách bệnh nhân theo ngày
@app.route('/api/patients', methods=['GET', 'POST'])
def get_patients():
    dates = request.args.get('date')
    appointment = Appointment_list.query.filter_by(date=dates).first()
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


@app.route('/api/available_patients', methods=['GET'])
def get_available_patients():
    date = request.args.get('date')
    patients = dao.get_patients_not_in_consultation(date)  # Lấy danh sách bệnh nhân chưa có phiếu khám

    return jsonify({'patients': patients})


@app.route('/api/confirm-day', methods=['POST'])
def confirm_day():
    date = request.args.get('date')
    isConfirm = dao.confirm_appointment(date)
    return jsonify(isConfirm)


@app.route('/api/create_bill', methods=['POST'])
def create_bill():
    data = request.get_json()

    try:
        # Lấy thông tin từ request
        medications = data['medications']
        consultation_id = data['consultation_id']  # Lấy ID của phiếu khám

        # Tính toán phí thuốc (medication_fee)
        medication_fee = 0
        for med in medications:
            # Lấy thông tin thuốc từ bảng Medication để lấy giá
            medication = Medication.query.get(med['medication_id'])
            if medication:
                price = medication.price
            else:
                return jsonify(
                    {'success': False, 'message': f"Không tìm thấy thuốc với ID {med['medication_id']}."}), 400

            quantity = med['quantity']
            medication_fee += price * quantity

        # Lấy giá trị consultation_fee từ bảng regulation
        regulation = Regulation.query.filter_by(name='Tiền khám').first()
        if regulation:
            consultation_fee = regulation.regulation
        else:
            # Nếu không có quy định, có thể gán giá trị mặc định
            consultation_fee = 100000  # Ví dụ: phí khám mặc định

        # Tính tổng (total) là tổng của medication_fee và consultation_fee
        total = medication_fee + consultation_fee

        # Tạo hóa đơn
        bill = Bill(
            date=datetime.now(),
            consultation_id=consultation_id,
            total=total,
            status=False,  # Hoặc True nếu hóa đơn đã được thanh toán
            medication_fee=medication_fee,
            consultation_fee=consultation_fee
        )
        db.session.add(bill)
        db.session.commit()

        # Lưu thông tin thuốc vào bảng BillMedication

        return jsonify({'success': True, 'message': 'Hóa đơn đã được tạo thành công.', 'bill_id': bill.id})

    except Exception as e:
        print(f"Error creating bill: {str(e)}")
        db.session.rollback()

        return jsonify({'success': False, 'message': str(e)}), 500


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
    new_patient = Patient(name=name, gender=GenderEnum[genderValue], birthday=f'{birth_year}-01-01', sdt=phone)

    isPatientExits = Patient.query.filter(Patient.sdt == new_patient.sdt).count() > 0
    if isPatientExits:
        return jsonify(error='patient already exists'), 409
    # Thêm vào cơ sở dữ liệu
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'Bệnh nhân đã được thêm thành công!', 'id': new_patient.id}), 201


@app.route('/api/medications', methods=['GET'])
def get_medications():
    medications = Medication.query.all()
    return jsonify([{
        'id': med.id,
        'name': med.name,
        'price': med.price,
        'instructions': med.instructions,
        'medication_unit_id': med.medication_unit_id
    } for med in medications])


@app.route('/api/medication_units/<int:unit_id>', methods=['GET'])
def get_medication_unit(unit_id):
    unit = Medication_units.query.filter_by(id=unit_id).first()
    if not unit:
        return jsonify({'error': 'Medication unit not found'}), 404
    return jsonify({'id': unit.id, 'unit': unit.unit})


@app.route('/api/consultation_form', methods=['GET', 'POST'])
def manage_consultation_form():
    if request.method == 'GET':
        consultation_form = Consultation_form.query.all()
        return jsonify([{
            'id': p.id,
            'date': p.date.strftime('%Y-%m-%d'),
            'patient_id': p.patient_id,
            'patient_name':Patient.query.get(p.patient_id).name,
            'symptoms': p.symptoms,
            'diagnosis': p.diagnosis
        } for p in consultation_form])

    if request.method == 'POST':
        data = request.json
        new_consultation_form = Consultation_form(
            date=data['date'],
            patient_id=data['patient_id'],
            symptoms=data['symptoms'],
            diagnosis=data['diagnosis']
        )
        db.session.add(new_consultation_form)
        db.session.commit()

        # Thêm thuốc vào bảng Medication_consultation
        for med in data['medications']:
            medication_consultation = Medication_consultation(
                quantity=med['quantity'],
                medication_id=med['medication_id'],
                consultation_id=new_consultation_form.id
            )
            db.session.add(medication_consultation)

        db.session.commit()
        return jsonify({'success': True, 'consultation_id': new_consultation_form.id}), 200


@app.route('/api/consultation_form/<int:id>', methods=['GET'])
def get_consultation_form(id):
    consultation_form = Consultation_form.query.get(id)
    if consultation_form:
        medications = Medication_consultation.query.filter_by(consultation_id=id).all()
        patient = Patient.query.get(consultation_form.patient_id)
        if not patient:
            return jsonify({'error': 'Bệnh nhân không tồn tại'}), 404

        return jsonify({
            'id': consultation_form.id,
            'date': consultation_form.date.strftime('%Y-%m-%d'),
            'patient_name': patient.name,
            'symptoms': consultation_form.symptoms,
            'diagnosis': consultation_form.diagnosis,
            'medications': [{
                'name': Medication.query.get(med.medication_id).name,
                'quantity': med.quantity
            } for med in medications]
        })
    return jsonify({'error': 'Không thể tìm thấy phiếu khám'}), 404


@app.route('/api/consultation_form/<int:id>', methods=['DELETE'])
def delete_prescription(id):
    prescription = Consultation_form.query.get(id)
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404

    # Xóa các thuốc liên quan
    Medication_consultation.query.filter_by(consultation_id=id).delete()
    db.session.delete(prescription)
    db.session.commit()
    return jsonify({'success': True}), 200







if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)
        # if not User.query.first():
        #     u = User(name='a', username='a', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #              user_role=UserEnum.ADMIN)
        #     db.session.add(u)
        #     db.session.commit()
        # if not Regulation.query.first():
        #     r = Regulation(name='Giới hạn bệnh nhân', regulation=40)
        #     r2 = Regulation(name='Tiền khám', regulation=100000)
        #     db.session.add(r)
        #     db.session.add(r2)
        #     db.session.commit()
