from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # e.g., admin, warden

# Hostel table
class Hostel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(200))

# Inspection form table
class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warden = db.Column(db.String(50), nullable=False)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    data = db.Column(db.JSON)  # All inspection answers as a JSON blob
