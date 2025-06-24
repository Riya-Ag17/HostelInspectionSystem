from app import app, db
from models import User

with app.app_context():
    users = [
        User(username='admin1', password='admin123', role='admin'),
        User(username='warden1', password='warden123', role='warden'),
        User(username='secy1', password='secy123', role='secretary')
    ]
    
    db.session.add_all(users)
    db.session.commit()
    print("✅ New users created.")
