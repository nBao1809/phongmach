from flask import render_template,request,redirect,url_for,flash
from flask_login import login_user, logout_user, login_required
from app import app,dao,login


@app.route('/')
def index():
    return render_template('index.html')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

# @app.route("/login", methods=['get', 'post'])
# def login_process():
#     if request.method.__eq__('POST'):
#         username = request.form.get('username')
#         password = request.form.get('password')
#         u = dao.auth_user(username=username, password=password)
#         if u:
#             login_user(u)
#
#             next = request.args.get('next')
#             return redirect(next if next else '/')
#
#     return render_template('login.html')

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


if __name__=='__main__':
    app.run(debug=True,port=5001)