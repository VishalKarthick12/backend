from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Uncategorized")
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(20), unique=True, nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string of cart items
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    
    # Delivery information
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    
    # Order status and timestamps
    status = db.Column(db.String(20), default="pending")
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery = db.Column(db.DateTime, nullable=True)
    
    # Additional information
    customer_name = db.Column(db.String(100), nullable=True)
    customer_email = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
