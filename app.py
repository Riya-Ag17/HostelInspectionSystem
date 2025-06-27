from flask import Flask, flash, render_template, redirect, url_for, request, session
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

            cur.execute("SELECT role FROM \"user\" WHERE username = %s AND password = %s", (username, password))
            result = cur.fetchone()

            if result:
                role = result[0]
                session['role'] = role
                session['username'] = username

                if role == 'admin':
                    return redirect('/admin_dashboard')
                elif role == 'secretary':
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
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            ''', (
                data['hostel_name'],
                data['warden_name'],
                datetime.now(),
                data.get('electricity_meter'),
                ', '.join(request.form.getlist('water_source')),
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
    if session.get('role') != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inspection ORDER BY submitted_on DESC")
    inspections = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    return render_template('admin_dashboard.html', inspections=inspections, columns=columns)

@app.route('/admin_logout')
def admin_logout():
    session.pop('role', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/secy_dashboard')
def secy_dashboard():
    if session.get('role') != 'secretary':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inspection ORDER BY submitted_on DESC")
    inspections = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    return render_template('secy_dashboard.html', inspections=inspections, columns=columns, zip=zip)

@app.route('/add_observation/<inspection_code>', methods=['GET', 'POST'])
def add_observation(inspection_code):
    if session.get('role') != 'secretary':
        return redirect('/login')

    if request.method == 'POST':
        secy_name = session.get('username') or "Secretary"
        comments = request.form['comments']
        rating = int(request.form['rating'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO secy_observations (inspection_id, secy_name, comments, rating)
            VALUES (%s, %s, %s, %s)
        """, (inspection_code, secy_name, comments, rating))
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/secy_dashboard')

    return render_template('add_observation.html', inspection_code=inspection_code)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            return render_template('add_user.html', message="❌ Passwords do not match!")

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO \"user\" (username, password, role) VALUES (%s, %s, %s)", 
                        (username, password, role))
            conn.commit()
            message = "✅ User added successfully!"
        except Exception as e:
            conn.rollback()
            message = f"❌ Error: {str(e)}"
        finally:
            cur.close()
            conn.close()

        return render_template('add_user.html', message=message)

    return render_template('add_user.html')

@app.route('/add_hostel', methods=['GET', 'POST'])
def add_hostel():
    if session.get('role') != 'admin':
        return redirect('/login')

    message = None  # initialize message

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check if hostel already exists
            cur.execute("SELECT * FROM hostel WHERE name = %s", (name,))
            existing_hostel = cur.fetchone()

            if existing_hostel:
                message = "⚠️ Hostel already exists. Please enter a different name."
            else:
                cur.execute("""
                    INSERT INTO hostel (name, location, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                """, (name, location, latitude, longitude))
                conn.commit()
                message = "✅ Hostel added successfully!"

            cur.close()
            conn.close()

        except Exception as e:
            message = f"❌ Error adding hostel: {e}"

    return render_template('add_hostel.html', message=message)

@app.route('/view_hostels')
def view_hostels():
    if session.get('role') != 'admin':
        return redirect('/')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM hostel ORDER BY id;")
    hostels = cur.fetchall()
    conn.close()

    return render_template('view_hostels.html', hostels=hostels)


@app.route('/view_users')
def view_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, hostel_id FROM \"user\" ORDER BY role, username;")
    users = cur.fetchall()
    conn.close()
    return render_template('view_users.html', users=users)


@app.route('/edit_hostel/<int:hostel_id>', methods=['GET', 'POST'])
def edit_hostel(hostel_id):
    if session.get('role') != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        try:
            cur.execute("""
                UPDATE hostel
                SET name = %s, location = %s, latitude = %s, longitude = %s
                WHERE id = %s
            """, (name, location, latitude, longitude, hostel_id))
            conn.commit()
            message = "✅ Hostel updated successfully!"
        except Exception as e:
            conn.rollback()
            message = f"❌ Error updating hostel: {e}"
        finally:
            cur.close()
            conn.close()

        return redirect('/view_hostels')  # Redirect to hostel list after update

    else:
        cur.execute("SELECT * FROM hostel WHERE id = %s", (hostel_id,))
        hostel = cur.fetchone()
        cur.close()
        conn.close()

        if hostel:
            return render_template('edit_hostel.html', hostel=hostel)
        else:
            return "Hostel not found.", 404


@app.route('/delete_hostel/<int:hostel_id>')
def delete_hostel(hostel_id):
    conn = psycopg2.connect(database="hostel_inspection", user="postgres", password="Berry", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("DELETE FROM hostel WHERE id = %s", (hostel_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_hostels'))

@app.route('/edit_user', methods=['POST'])
def edit_user():
    user_id = request.form['id']
    username = request.form['username']
    role = request.form['role']
    hostel_id = request.form['hostel_id']

    # Convert empty hostel_id to None (or null) if it's optional
    hostel_id = int(hostel_id) if hostel_id.strip() else None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE "user"
        SET username = %s, role = %s, hostel_id = %s
        WHERE id = %s
    """, (username, role, hostel_id, user_id))
    conn.commit()
    conn.close()
    return redirect('/view_users')


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM "user" WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/view_users')







if __name__ == '__main__':
    app.run(debug=True)
