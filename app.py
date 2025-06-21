from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

from functools import wraps

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return "Unauthorized access", 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Load users from JSON
def load_users():
    with open('users.json') as f:
        return json.load(f)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/warden-form')
@login_required(role='warden')
def warden_form():
    return f"""
        Welcome Warden {session.get('username')}! This is your form page.<br>
        <a href='/logout'>Logout</a>
    """

@app.route('/secy-dashboard')
@login_required(role='secretary')
def secy_dashboard():
    return f"""
        Welcome Secretary {session.get('username')}! This is your dashboard.<br>
        <a href='/logout'>Logout</a>
    """

@app.route('/admin-dashboard')
@login_required(role='admin')
def admin_dashboard():
    return f"""
        Welcome Admin {session.get('username')}! This is your dashboard.<br>
        <a href='/logout'>Logout</a>
    """


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/warden-form', methods=['GET', 'POST'])
@login_required(role='warden')
def warden_form():
    if request.method == 'POST':
        bathroom_clean = request.form.get('bathroom_clean')
        lights_working = request.form.get('lights_working')
        water_available = request.form.get('water_available')

        # For now, just print to console (simulate saving)
        print("Form submitted by:", session['username'])
        print("Bathroom Clean:", bathroom_clean)
        print("Lights Working:", lights_working)
        print("Water Available:", water_available)

        flash('Inspection submitted successfully!', 'success')
        return redirect(url_for('warden_form'))

    return render_template('warden_form.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']

                # Role-based redirects
                if user['role'] == 'warden':
                    return redirect(url_for('warden_form'))
                elif user['role'] == 'secretary':
                    return redirect(url_for('secy_dashboard'))
                elif user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
        
        flash('Invalid username or password.')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

