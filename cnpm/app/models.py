import hashlib
from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin


class UserEnum(RoleEnum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    CASHIER = "cashier"


class GenderEnum(RoleEnum):
    MALE = "nam"
    FEMALE = "nữ"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    user_role = db.Column(Enum(UserEnum), nullable=False)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum(GenderEnum), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    sdt = db.Column(db.String(20), nullable=False)

    def toDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender.value,
            "birthday": self.birthday.strftime("%Y-%m-%d"),
            "sdt": self.sdt,
        }


class Medication_units(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit = db.Column(db.String(50), nullable=False)
    medication = relationship("Medication", backref="unit_medications", lazy=True)


class Appointment_list(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    status = db.Column(db.Boolean, nullable=False,default=0)
    total = db.Column(db.Integer, nullable=True)


class Patient_Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment_list.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    medication_unit_id = db.Column(db.Integer, ForeignKey("medication_units.id"), nullable=False, index=True)
    medication_consultations = relationship("Medication_consultation", backref="medication_units", lazy=True,
                                            cascade="all, delete-orphan")
    instructions = db.Column(db.Text, nullable=False)

    def __str__(self):
        return self.name


class Consultation_form(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    patient_id = db.Column(db.Integer, ForeignKey("patient.id"), nullable=False, index=True)
    # chan doan
    diagnosis = db.Column(db.Text, nullable=False)
    #   trieu chung
    symptoms = db.Column(db.Text, nullable=False)
    medication_consultations = relationship("Medication_consultation", backref="consultation")


class Medication_consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    medication_id = db.Column(db.Integer, ForeignKey("medication.id"), nullable=False, index=True)
    consultation_id = db.Column(db.Integer, ForeignKey("consultation_form.id"), nullable=False, index=True)


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    consultation_id = db.Column(db.Integer, ForeignKey("consultation_form.id"), nullable=False, index=True)
    medication_fee=db.Column(db.Integer, nullable=False)
    consultation_fee=db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)


class Regulation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    regulation = db.Column(db.Integer, nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        # # Tạo người dùng giả
        # # Tạo bệnh nhân giả
        # patient1 = Patient(name="Nguyen Van A", gender=GenderEnum.MALE, birthday=datetime(1990, 1, 1), sdt="0123456789")
        # patient2 = Patient(name="Tran Thi B", gender=GenderEnum.FEMALE, birthday=datetime(1995, 5, 5), sdt="0987654321")
        #
        # db.session.add(patient1)
        # db.session.add(patient2)
        #
        # # Tạo đơn vị thuốc giả
        # unit1 = Medication_units(unit="Viên")
        # unit2 = Medication_units(unit="Chai")
        #
        # db.session.add(unit1)
        # db.session.add(unit2)
        #
        # # Tạo thuốc giả
        # medication1 = Medication(name="Paracetamol", price=10000, medication_unit_id=1,
        #                          instructions="Uống 1 viên mỗi 6 giờ.")
        # medication2 = Medication(name="Ibuprofen", price=15000, medication_unit_id=2,
        #                          instructions="Uống 1 viên mỗi 8 giờ.")
        #
        # db.session.add(medication1)
        # db.session.add(medication2)
        #
        # # Tạo danh sách hẹn giả
        # appointment1 = Appointment_list(date=datetime.now(), status=1, total=0)
        # appointment2 = Appointment_list(date=datetime.now() + timedelta(days=1), status=0, total=0)
        #
        # db.session.add(appointment1)
        # db.session.add(appointment2)
        #
        # # Commit các thay đổi để lưu vào cơ sở dữ liệu
        # db.session.commit()
        #
        # # Tạo mối quan hệ giữa bệnh nhân và đơn hẹn
        # patient_appointment1 = Patient_Appointment(appointment_id=1, patient_id=1)
        # patient_appointment2 = Patient_Appointment(appointment_id=2, patient_id=2)
        #
        # db.session.add(patient_appointment1)
        # db.session.add(patient_appointment2)
        #
        # # Tạo phiếu khám giả
        # consultation1 = Consultation_form(date=datetime.now(), patient_id=1, diagnosis="Cảm cúm", symptoms="Sốt, ho")
        # consultation2 = Consultation_form(date=datetime.now() + timedelta(days=1), patient_id=2, diagnosis="Đau đầu",
        #                                   symptoms="Đau đầu, chóng mặt")
        #
        # db.session.add(consultation1)
        # db.session.add(consultation2)
        #
        # # Commit các thay đổi để lưu vào cơ sở dữ liệu
        # db.session.commit()
        #
        # # Tạo hóa đơn giả
        # bill1 = Bill(date=datetime.now(), consultation_id=1, medication_fee=10000, consultation_fee=20000, total=30000,
        #              status=1)
        # bill2 = Bill(date=datetime.now() + timedelta(days=1), consultation_id=2, medication_fee=15000,
        #              consultation_fee=25000, total=40000, status=0)
        #
        # db.session.add(bill1)
        # db.session.add(bill2)
        #
        # # Commit hóa đơn
        # db.session.commit()