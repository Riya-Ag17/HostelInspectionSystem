from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# PostgreSQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/hostel_inspection'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import models (ensure models.py is in the same directory)
from models import User, Inspection

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'warden':
                return redirect(url_for('warden_form'))
            elif user.role == 'secretary':
                return redirect(url_for('secy_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/warden-form', methods=['GET', 'POST'])
def warden_form():
    if 'username' not in session or session.get('role') != 'warden':
        return redirect(url_for('login'))

    if request.method == 'POST':
        form_data = {
            'hostel_name': request.form.get('hostel_name'),
            'month': request.form.get('month'),
            'electricity_status': request.form.get('electricity_status'),
            'drinking_water_sources': ','.join(request.form.getlist('drinking_water_sources')),
            'water_inspection_date': request.form.get('water_inspection_date'),
            'paint_inspection_date': request.form.get('paint_inspection_date'),
            'pest_control_date': request.form.get('pest_control_date'),
            'maintenance_pending': request.form.get('maintenance_pending'),
            'last_cleaned_outside': request.form.get('last_cleaned_outside'),
            'last_cleaned_corridor': request.form.get('last_cleaned_corridor'),
            'last_cleaned_toilet': request.form.get('last_cleaned_toilet'),
            'last_cleaned_kitchen': request.form.get('last_cleaned_kitchen'),
            'last_cleaned_store': request.form.get('last_cleaned_store'),
            'last_cleaned_library': request.form.get('last_cleaned_library'),
            'last_cleaned_warden_room': request.form.get('last_cleaned_warden_room'),
            'utensils_provided': request.form.get('utensils_provided'),
            'utensils_in_use': request.form.get('utensils_in_use'),
            'utensils_damaged': request.form.get('utensils_damaged'),
            'utensils_washing_status': request.form.get('utensils_washing_status'),
            'utensils_storage_status': request.form.get('utensils_storage_status'),
            'meal_prep_time': request.form.get('meal_prep_time'),
            'meals_served': request.form.get('meals_served'),
            'meal_complaints': request.form.get('meal_complaints'),
            'meal_wastage': request.form.get('meal_wastage'),
            'cameras_installed': request.form.get('cameras_installed'),
            'cameras_working': request.form.get('cameras_working'),
            'camera_installation_date': request.form.get('camera_installation_date'),
            'camera_visual_computer': request.form.get('camera_visual_computer'),
            'gas_cylinders_status': request.form.get('gas_cylinders_status'),
            'secure_storage_status': request.form.get('secure_storage_status'),
            'loose_wires_status': request.form.get('loose_wires_status'),
            'visitor_register': request.form.get('visitor_register'),
            'staff_attendance_register': request.form.get('staff_attendance_register'),
            'submitted_by': session['username'],
            'submitted_on': datetime.utcnow()
        }

        inspection = Inspection(**form_data)
        db.session.add(inspection)
        db.session.commit()

        flash('Inspection data submitted successfully.')
        return redirect(url_for('warden_form'))

    return render_template('warden_form.html')

@app.route('/secy-dashboard')
def secy_dashboard():
    if 'username' not in session or session.get('role') != 'secretary':
        return redirect(url_for('login'))

    inspections = Inspection.query.order_by(Inspection.submitted_on.desc()).all()
    return render_template('secy_dashboard.html', inspections=inspections)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    inspections = Inspection.query.order_by(Inspection.submitted_on.desc()).all()
    return render_template('admin_dashboard.html', inspections=inspections)

if __name__ == '__main__':
    app.run(debug=True)
