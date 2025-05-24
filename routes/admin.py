from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.get_id().startswith('admin-'):
        return render_template('admin/dashboard.html', admin=current_user)
    flash('Access denied.', 'danger')
    return redirect(url_for('index'))
