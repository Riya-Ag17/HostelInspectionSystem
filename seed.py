from app import app
from models import db, User, Hostel

with app.app_context():
    # Add users
    if not User.query.first():
        admin = User(username='admin1', password='adminpass', role='admin')
        warden = User(username='warden1', password='wardenpass', role='warden')
        db.session.add_all([admin, warden])
    
    # Add hostels
    if not Hostel.query.first():
        h1 = Hostel(name='Ganga Hostel', location='North Campus')
        h2 = Hostel(name='Yamuna Hostel', location='South Campus')
        db.session.add_all([h1, h2])

    db.session.commit()
    print("✅ Sample data inserted.")
