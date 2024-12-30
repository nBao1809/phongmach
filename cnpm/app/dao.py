import hashlib

from app import db
from app.models import User, Patient, Appointment_list, Patient_Appointment, Consultation_form


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

    return new_appointment  # Trả về đối tượng cuộc hẹn mới


def get_patient_appointment(patient_id, appointment_id):
    return Patient_Appointment.query.filter(Patient_Appointment.appointment_id == appointment_id,
                                            Patient_Appointment.patient_id == patient_id).first()


def get_patients_not_in_consultation(date):
    if not date:
        return []

    # Lấy danh sách bệnh nhân có phiếu khám trong ngày đã chọn
    consultations = Consultation_form.query.filter_by(date=date).all()
    consulted_patient_ids = {consultation.patient_id for consultation in consultations}  # Dùng set để kiểm tra nhanh

    # Lấy tất cả cuộc hẹn có status = 1 cho ngày đã chọn
    appointments = Appointment_list.query.filter_by(date=date, status=1).all()

    patients = []

    # Lặp qua tất cả các cuộc hẹn có status = 1
    for appointment in appointments:
        # Lấy bệnh nhân của mỗi cuộc hẹn
        patient_appointments = Patient_Appointment.query.filter_by(appointment_id=appointment.id).all()
        for patient_appointment in patient_appointments:
            # Lấy thông tin bệnh nhân
            patient = Patient.query.get(patient_appointment.patient_id)
            if patient and patient.id not in consulted_patient_ids:
                patients.append(patient)
                consulted_patient_ids.add(patient.id)  # Thêm bệnh nhân vào danh sách đã tham khảo để tránh trùng lặp

    # Chuyển dữ liệu bệnh nhân thành dạng dict để trả về API
    patients_data = [patient.toDict() for patient in patients]
    return patients_data


def make_appointment(patient_id, appointment):
    # Kiểm tra xem bệnh nhân và cuộc hẹn có tồn tại hay không
    patient = Patient.query.get(patient_id)
    if not patient:
        return {'error': 'Patient not found'}
    if not appointment:
        return {'error': 'Appointment not found'}
    # Tạo một đối tượng Patient_Appointment mới
    new_patient_appointment = Patient_Appointment(appointment_id=appointment.id, patient_id=patient.id)

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


def get_all_patients_consultion(date):
    patients = []
    if not date:
        return patients
    p_consultation_form = Consultation_form.query.filter_by(date=date).all()
    # Lặp qua từng cuộc hẹn để lấy bệnh nhân
    for p in p_consultation_form:
        patient = Patient.query.get(p.patient_id)
        if patient:  # Kiểm tra nếu bệnh nhân tồn tại
            patients.append(patient)
    patients_data = [patient.toDict() for patient in patients]
    return patients_data


def get_date():
    appointments = Appointment_list.query.order_by(Appointment_list.date, Appointment_list.status == 1).all()
    date = [appointment.date for appointment in appointments if appointment.status == 0]
    return sorted(date)


def get_date_status_1():
    # Lấy tất cả các cuộc hẹn có status = 1
    appointments = Appointment_list.query.filter(Appointment_list.status == 1).all()

    # Danh sách các ngày có bệnh nhân và không có phiếu khám
    date_with_patients = []

    for appointment in appointments:
        # Lấy danh sách bệnh nhân của cuộc hẹn
        patient_appointments = Patient_Appointment.query.filter_by(appointment_id=appointment.id).all()

        # Kiểm tra nếu cuộc hẹn có bệnh nhân và bệnh nhân chưa có phiếu khám
        for patient_appointment in patient_appointments:
            # Kiểm tra xem bệnh nhân đã có phiếu khám chưa
            consultation = Consultation_form.query.filter_by(patient_id=patient_appointment.patient_id,
                                                             date=appointment.date).first()

            if not consultation:  # Nếu bệnh nhân chưa có phiếu khám
                date_with_patients.append(appointment.date)
                break  # Không cần kiểm tra thêm bệnh nhân cho cuộc hẹn này

    # Trả về danh sách các ngày sắp xếp theo thứ tự tăng dần
    return sorted(date_with_patients)


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


def get_patient_by_id(id):
    return Patient.query.get(id)
