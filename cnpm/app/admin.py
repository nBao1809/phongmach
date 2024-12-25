import hashlib

from app.models import Medication, Medication_units, Consultation_fee, User, UserEnum, DailyPatientLimit
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


admin = Admin(app=app, name='Phòng mạch', template_mode='bootstrap4', index_view=MyAdminIndexView())


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserEnum.ADMIN)

    def on_model_change(self, form, model, is_created):
        if is_created:
            # Nếu đây là một người dùng mới, bạn sẽ hash mật khẩu trước khi lưu
            if form.password.data:
                model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())

            # Gán vai trò mặc định nếu cần
            if not model.user_role:
                model.user_role = UserEnum.USER
        else:
            # Nếu người dùng đã tồn tại và thay đổi thông tin, hash lại mật khẩu nếu có thay đổi
            if form.password.data:
                model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())

        return super().on_model_change(form, model, is_created)


class MedicationView(AdminView):
    column_list = ['name', 'price']
    column_searchable_list = ['name']
    column_editable_list = ['name','price']
    can_export = True
    column_labels = {
        'name':'Tên thuốc',
        'price':'Giá bán',
    }


class Medication_unitsView(AdminView):
    column_list = ['unit']
    column_editable_list = ['unit']
    column_labels = {
        'unit':'Đơn vị'
    }


class Consultation_feeView(AdminView):
    column_list = ['fee']
    column_editable_list = ['fee']
    column_labels = {
        'fee':'Phí khám bệnh'
    }


class DailyPatientLimitView(AdminView):
    column_list = ['max_patients']
    column_editable_list = ['max_patients']
    column_labels = {
        'max_patients': 'Giới hạn bệnh nhân'
    }


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')



admin.add_view(MedicationView(Medication, db.session,name='Thuốc'))
admin.add_view(Medication_unitsView(Medication_units, db.session,name="Đơn vị"))
admin.add_view(Consultation_feeView(Consultation_fee, db.session,name="Phí khám bệnh"))
admin.add_view(DailyPatientLimitView(DailyPatientLimit, db.session,name="Giới hạn bệnh nhân"))
admin.add_view(AdminView(User, db.session))
admin.add_view(LogoutView(name='Đăng xuất'))
