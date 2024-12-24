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


class MedicationView(AdminView):
    column_list = ['name', 'price']
    column_searchable_list = ['name']
    column_editable_list = ['name','price']
    can_export = True


class Medication_unitsView(AdminView):
    column_list = ['unit']
    column_editable_list = ['unit']


class Consultation_feeView(AdminView):
    column_list = ['fee']
    column_editable_list = ['fee']


class DailyPatientLimitView(AdminView):
    column_list = ['max_patients']
    column_editable_list = ['max_patients']



class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


# class StatsView(AuthenticatedView):
#     @expose('/')
#     def index(self):
#
#         return self.render('admin/stats.html',
#                            stats=dao.revenue_stats_by_products(),
#                            stats2=dao.revenue_stats_by_time())


admin.add_view(MedicationView(Medication, db.session))
admin.add_view(Medication_unitsView(Medication_units, db.session))
admin.add_view(Consultation_feeView(Consultation_fee, db.session))
admin.add_view(DailyPatientLimitView(DailyPatientLimit, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(LogoutView(name='Đăng xuất'))
