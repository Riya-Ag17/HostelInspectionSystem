from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
from datetime import datetime
import uuid


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="hostel_inspection",
        user="postgres",
        password="Berry"
    )

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Query the user from your user table
            cur.execute("SELECT role FROM \"user\" WHERE username = %s AND password = %s", (username, password))
            result = cur.fetchone()

            if result:
                role = result[0]
                session['role'] = role

                if role == 'admin':
                    return redirect('/admin_dashboard')
                elif role == 'secy':
                    return redirect('/secy_dashboard')
                elif role == 'warden':
                    return redirect('/warden_form')
                else:
                    return "Unknown role."

            else:
                return "Invalid username or password."

        except Exception as e:
            return f"Login error: {e}"

        finally:
            cur.close()
            conn.close()

    return render_template('login.html')


@app.route('/warden_form', methods=['GET', 'POST'])
def warden_form():
    if request.method == 'POST':
        data = request.form
        contact_number = data.get('contact_number')
        if not contact_number or not contact_number.isdigit() or len(contact_number) != 10:
            return "Invalid contact number. Please enter exactly 10 digits."


        try:
            conn = get_db_connection()
            cur = conn.cursor()

            inspection_code = str(uuid.uuid4())


            cur.execute('''
                INSERT INTO inspection (
                    hostel_id,
                    submitted_by,
                    submitted_on,
                    electricity_status,
                    drinking_water_sources,
                    water_inspection_date,
                    paint_inspection_date,
                    pest_control_date,
                    maintenance_pending,
                    last_cleaned_outside,
                    last_cleaned_corridor,
                    last_cleaned_toilet,
                    last_cleaned_kitchen,
                    last_cleaned_store,
                    last_cleaned_library,
                    last_cleaned_warden_room,
                    utensils_provided,
                    utensils_in_use,
                    utensils_damaged,
                    utensils_washing_status,
                    utensils_storage_status,
                    meal_prep_time,
                    meals_served,
                    meal_complaints,
                    meal_wastage,
                    cameras_installed,
                    cameras_working,
                    camera_installation_date,
                    camera_visual_computer,
                    gas_cylinders_status,
                    secure_storage_status,
                    loose_wires_status,
                    visitor_register,
                    staff_attendance_register,
                    contact_number,
                    inspection_code
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s
                )
            ''', (
                data['hostel_name'],
                data['warden_name'],
                datetime.now(),
                data.get('electricity_meter'),
                ', '.join(request.form.getlist('water_source')),# This will only send one source; multi-source needs handling
                data.get('water_tank_cleaning'),
                data.get('painting_date'),
                data.get('pest_control_date'),
                data.get('pending_gaps'),
                data.get('cleaning_outside'),
                data.get('cleaning_corridor'),
                data.get('cleaning_toilets'),
                data.get('cleaning_kitchen'),
                data.get('cleaning_store'),
                data.get('cleaning_library'),
                data.get('cleaning_warden_room'),
                data.get('utensils_provided'),
                data.get('utensils_in_use'),
                data.get('utensils_damaged'),
                data.get('washing_status'),
                data.get('storage_condition'),
                data.get('meal_time'),
                data.get('meals_served'),
                data.get('meal_complaints'),
                data.get('food_wastage'),
                data.get('cameras_installed'),
                data.get('cameras_working'),
                data.get('camera_installation_date'),
                data.get('visuals_available'),
                data.get('gas_cylinders'),
                data.get('secure_storage'),
                data.get('wiring_issues'),
                data.get('visitor_register'),
                data.get('staff_attendance'),
                int(contact_number),
                inspection_code
            ))

            conn.commit()
            cur.close()
            conn.close()

            return f"Inspection submitted successfully. Code: {inspection_code}"

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('warden_form.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return "Admin Dashboard"

@app.route('/secy_dashboard')
def secy_dashboard():
    return "Secretary Dashboard"

if __name__ == '__main__':
    app.run(debug=True)
