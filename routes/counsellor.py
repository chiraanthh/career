from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import CareerCounselor, db
from datetime import datetime

counsellor_bp = Blueprint('counsellor', __name__, url_prefix='/counsellor')

@counsellor_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        specialization = request.form.get('specialization')
        qualification = request.form.get('qualification')
        years_of_experience = request.form.get('years_of_experience')
        bio = request.form.get('bio')

        if CareerCounselor.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('counsellor/register.html')

        counsellor = CareerCounselor(
            email=email,
            first_name=first_name,
            last_name=last_name,
            specialization=specialization,
            qualification=qualification,
            years_of_experience=years_of_experience,
            bio=bio,
            availability_status=True,
            date_registered=datetime.utcnow()
        )
        counsellor.set_password(password)

        try:
            db.session.add(counsellor)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'danger')
            return render_template('counsellor/register.html')

    return render_template('counsellor/register.html')

@counsellor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.get_id().startswith('counsellor-'):
        return render_template('counsellor/dashboard.html', counsellor=current_user)
    flash('Access denied.', 'danger')
    return redirect(url_for('index'))
