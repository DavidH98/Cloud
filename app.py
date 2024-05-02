import io
from flask import Flask, render_template, redirect, url_for, flash, session, request, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from db import DB   
from FileChunker import Chunker
from helper import calc_storage, create_file_object, format_file_data
import re
import pymysql
from flask import flash
from passlib.hash import pbkdf2_sha256

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xc6\x89\xc2z\xae\x12)\x13XP\xafYE_Z\x8d\x14\x90\xa5\x19\xbe\x9a\xc2\xa0'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://root:@localhost/cloud'
db = SQLAlchemy(app)
db_instance = DB()
chunker = Chunker(chunk_size=10240)

class LoginForm(FlaskForm):
    email = StringField('l_email', validators=[DataRequired(), Email()])
    password = PasswordField('l_password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    email = StringField('s_email', validators=[DataRequired(), Email()])
    username = StringField('s_username', validators=[DataRequired()])
    password = PasswordField('s_password', validators=[DataRequired()])
    submit = SubmitField('Sign up')

class PasswordResetForm(FlaskForm):
    email = StringField('p_email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset password')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    __tablename__ = 'users'

@app.route('/', methods=['GET', 'POST'])
def index():
    # home
    animated_css = "https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.5.2/animate.min.css"
    external_font = "https://fonts.googleapis.com/css?family=Lato:300,400,700,300italic,400italic,700italic&amp;display=swap"

    return render_template('index.html', animated_css=animated_css, external_font=external_font)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    external_font = "https://fonts.googleapis.com/css?family=Lato:300,400,700,300italic,400italic,700italic&amp;display=swap"
    mat_design = "https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/5.3.45/css/materialdesignicons.css"
    animate = "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"
    box_icon = "https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css"
    jquery = "https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"

    login_form = LoginForm()
    signup_form = SignupForm()
    reset_form = PasswordResetForm()

    if signup_form.validate_on_submit():
        email = signup_form.email.data
        username = signup_form.username.data
        password = signup_form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            if re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",password):
                new_user = User(
                    id = db_instance.get_last_id("users","id")+1,
                    username=username,
                    email=email,
                    password_hash = pbkdf2_sha256.hash(password)
                )
                db.session.add(new_user)
                db.session.commit()            
                login_user(User.query.filter_by(email=email).first())
                return redirect(url_for('panel'))
            else:
                flash('Your password isn\'t strong enough', 'danger')
        else:
            flash('User already exist', 'danger')
            print('User already exist')

    elif login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if pbkdf2_sha256.verify(password, user.password_hash):

                login_user(user)
                return redirect(url_for('panel'))
            else:
                print('Login failed. Password not match.')
                flash('Login failed. Password not match.', 'danger')
        else:
            print('Login failed. Email not found.')
            flash('Login failed. Email not found.', 'danger')

    elif reset_form.validate_on_submit():
        print("here - 85")
    
    return render_template('login.html', mat_design=mat_design, animate=animate, external_font=external_font, box_icon=box_icon, jquery=jquery, login_form=login_form, signup_form=signup_form, reset_form=reset_form)


@app.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
    external_font = "https://fonts.googleapis.com/css?family=Lato:300,400,700,300italic,400italic,700italic&amp;display=swap"
    mat_design = "https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/5.3.45/css/materialdesignicons.css"
    animate = "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"
    box_icon = "https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css"
    jquery = "https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"
    files = format_file_data(db_instance.get_files_by_user_id(current_user.id))
    storage = calc_storage(files)
    
    if request.method == "POST":
        if 'fileInput' in request.files:
            uploaded_file = request.files['fileInput']
            chunker.chunk_file(uploaded_file.read(), uploaded_file.filename, current_user.id)
            files = format_file_data(db_instance.get_files_by_user_id(current_user.id))
            print(uploaded_file.filename + " Has been uploaded")
            return redirect(url_for('panel'))
    
    return render_template('panel.html' , mat_design=mat_design, animate=animate, external_font=external_font, box_icon=box_icon, jquery=jquery, login_info=current_user, files=files, storage=storage)

@app.route('/download/<file_id>')
@login_required
def download_file(file_id):
    if db_instance.has_file(file_id, current_user.id):
        file_data, file_name = chunker.rechunk_file(file_id)
        file_obj, mime_type = create_file_object(file_data, file_name)
        return send_file(
            file_obj,
            as_attachment = True,
            download_name = file_name,
            mimetype = mime_type
        )
    return redirect(url_for('panel'))

@app.route('/delete/<file_id>')
@login_required
def delete_file(file_id):
    if db_instance.has_file(file_id, current_user.id):
        try:
            db_instance.delete_file(file_id)
        finally:
            redirect(url_for('panel'))
            return redirect(url_for('panel'))
    return redirect(url_for('panel'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="5000")
