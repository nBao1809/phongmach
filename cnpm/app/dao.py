import hashlib

from flask import jsonify

from app import db
from app.models import User, Patient, Appointment_list, Patient_Appointment, Bill, Consultation_form


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def get_user_by_id(id):
    return User.query.get(id)


def get_patient_by_phone(phone):
    return Patient.query.filter(Patient.sdt.__eq__(phone)).first()



def add_new_patient(patient):
    db.session.add(patient)
    db.session.commit()
    return patient  # Trả về đối tượng bệnh nhân đã được thêm


def add_appointment_list(date):
    # Kiểm tra xem cuộc hẹn đã tồn tại cho ngày này chưa
    existing_appointment = Appointment_list.query.filter(Appointment_list.date == date).first()
    if existing_appointment:
        return existing_appointment


    # Tạo một đối tượng Appointment_list mới
    new_appointment = Appointment_list(date=date, status=0)

    # Thêm đối tượng vào cơ sở dữ liệu
    db.session.add(new_appointment)
    db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu

    return {
        'id':new_appointment.id,
        'date':new_appointment.date,
        'status':new_appointment.status
    }  # Trả về đối tượng cuộc hẹn mới

def get_patient_appointment(patient_id, appointment_id):
    return Patient_Appointment.query.filter(
        (Patient_Appointment.appointment_id == appointment_id) & (Patient_Appointment.patient_id == patient_id)).first()


def make_appointment(patient_id, appointment):
    # Kiểm tra xem bệnh nhân và cuộc hẹn có tồn tại hay không
    patient = Patient.query.get(patient_id)
    if not patient:
        return {'error': 'Patient not found'}
    if not appointment:
        return {'error': 'Appointment not found'}

    # Tạo một đối tượng Patient_Appointment mới
    new_patient_appointment =Patient_Appointment(appointment_id=appointment.id, patient_id=patient_id)

    # Thêm đối tượng vào cơ sở dữ liệu
    db.session.add(new_patient_appointment)
    db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    # lấy patient_appointment vừa thêm vào
    patient_appointment = get_patient_appointment(patient_id=patient.id, appointment_id=appointment.id)
    return {
        'patient_appointment_id': patient_appointment.id,
        'patient_id': patient.id,
        'appointment_id': appointment.id,
        'status': appointment.status,
        'date': appointment.date,
    }  # Trả về đối tượng Patient_Appointment mới


def get_all_patients(appointment):
    patients = []
    if not appointment:
        return patients
    patients_appointments = Patient_Appointment.query.filter_by(appointment_id=appointment.id).all()
    # Lặp qua từng cuộc hẹn để lấy bệnh nhân
    for p in patients_appointments:
        patient = Patient.query.get(p.patient_id)
        if patient:  # Kiểm tra nếu bệnh nhân tồn tại
            patients.append(patient)
    patients_data = [patient.toDict() for patient in patients]
    return patients_data


def get_date():
    appointments = Appointment_list.query.order_by(Appointment_list.date).all()
    date = [appointment.date for appointment in appointments if appointment.status == 0]
    return sorted(date)


def delete_patient_in_appointment(patient_id, appointment_id):
    patient_appointment = Patient_Appointment.query.filter_by(appointment_id=appointment_id,
                                                              patient_id=patient_id).first()
    if not patient_appointment:
        return {'error': 'Không tìm thấy bản ghi bệnh nhân trong cuộc hẹn.'}
    db.session.delete(patient_appointment)
    appointment = Appointment_list.query.get(appointment_id)
    patient_appointment_check = Patient_Appointment.query.filter(appointment_id=appointment_id).first()
    if not patient_appointment_check:
        db.session.delete(appointment)
    db.session.commit()
    return {'success': 'Xóa thành công'}


def confirm_appointment(date):
    appointments = Appointment_list.query.filter_by(date=date).first()
    appointments.status = True
    db.session.commit()
    return {'success': True}


def update_patient(id, name, birthday, gender, sdt):
    patient = Patient.query.get(id)
    if patient is None:
        return {'error': 'Bệnh nhân không tồn tại!'}
    patient.name = name
    patient.birthday = birthday
    patient.sdt = sdt
    patient.gender = gender
    db.session.commit()
    return {'message': 'Bệnh nhân đã được sửa thành công!'}


def get_all_bill():
    bill_dict={}
    bills = Bill.query.all()
    for b in bills:
        consultation=Consultation_form.query.get(b.consultation_id)
        patient=Patient.query.get(consultation.patient_id)
        bill_dict[b.id] = {
            'id': b.id,
            'patient_name': patient.name,
            'date': b.date.strftime("%Y-%m-%d %H:%M:%S"),
            'medication_fee': b.medication_fee,
            'consultation_fee': b.consultation_fee,
            'total': b.total,
            'status': b.status,
        }

    return bill_dict





def confirm_bill(bill_id):
    bill = Bill.query.get(bill_id)
    if bill is None:
        return {'error':"Lỗi khi xác nhận hóa đơn"}
    bill.status = True
    db.session.commit()
    return {'success': "Xác nhận thành công hóa đơn"}