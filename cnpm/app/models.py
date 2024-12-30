import hashlib

from sqlalchemy import Column, ForeignKey, Enum
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
    user_role = Column(Enum(UserEnum), nullable=False)


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
            "birthday": self.birthday.year,
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
    date = db.Column(db.DateTime, nullable=False)
    patient_id = db.Column(db.Integer, ForeignKey("patient.id"), nullable=False, index=True)
    # chan doan
    diagnosis = db.Column(db.String(255), nullable=False)
    #   trieu chung
    symptoms = db.Column(db.String(255), nullable=False)
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
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)


class Regulation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    regulation = db.Column(db.Integer, nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
