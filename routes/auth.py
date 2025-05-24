from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import Student, CareerCounselor, Administrator
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

auth_bp = Blueprint('auth', __name__)
db = SQLAlchemy()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Try to find user in each type of user table
        user = Student.query.filter_by(email=email).first()
        user_type = 'student'
        
        if not user:
            user = CareerCounselor.query.filter_by(email=email).first()
            user_type = 'counsellor'
            
        if not user:
            user = Administrator.query.filter_by(email=email).first()
            user_type = 'admin'

        if user is None:
            flash('No account found with that email.', 'danger')
        elif not user.check_password(password):
            flash('Incorrect password.', 'danger')
        else:
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            if user_type == 'student':
                return redirect(url_for('student.dashboard'))
            elif user_type == 'counsellor':
                return redirect(url_for('counselor.dashboard'))
            elif user_type == 'admin':
                return redirect(url_for('admin.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index')) 