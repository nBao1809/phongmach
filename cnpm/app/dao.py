import hashlib

from flask import jsonify

from app import db
from app.models import User, Patient, Appointment_list, Patient_Appointment


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

# def add_shedule(date):
#     limit=DailyPatientLimit.query.first()

def add_new_patient(patient):
    db.session.add(patient)
    db.session.commit()
    return patient  # Trả về đối tượng bệnh nhân đã được thêm


def add_appointment_list(date):

    # Kiểm tra xem cuộc hẹn đã tồn tại cho ngày này chưa
    existing_appointment = Appointment_list.query.filter(Appointment_list.date == date).first()
    if existing_appointment:
        return {"error": "Đã có danh sách hẹn trong ngày"}

    # Tạo một đối tượng Appointment_list mới
    new_appointment = Appointment_list(date=date, status=False)

    # Thêm đối tượng vào cơ sở dữ liệu
    db.session.add(new_appointment)
    db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu

    return {
        'id':new_appointment.id,
        'date':new_appointment.date,
        'status':new_appointment.status
    }  # Trả về đối tượng cuộc hẹn mới




def make_appointment(patient_id, appointment):

    # Tạo một đối tượng Patient_Appointment mới
    new_patient_appointment =Patient_Appointment(appointment_id=appointment.id, patient_id=patient_id)

    # Thêm đối tượng vào cơ sở dữ liệu
    db.session.add(new_patient_appointment)
    db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    return {
        'patient_id': patient_id,
        'appointment_id': appointment.id,
        'status': appointment.status,
        'date': appointment.date,
    }  # Trả về đối tượng Patient_Appointment mới
