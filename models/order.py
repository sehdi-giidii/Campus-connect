from extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id           = db.Column(db.Integer, primary_key=True)
    order_ref    = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service      = db.Column(db.String(20), nullable=False)
    items        = db.Column(db.Text, nullable=False)
    total        = db.Column(db.Integer, nullable=False)
    status       = db.Column(db.String(20), default='pending')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    scooty_id    = db.Column(db.String(10), nullable=True)
    scooty_model = db.Column(db.String(50), nullable=True)
    rental_type  = db.Column(db.String(10), nullable=True)
    duration     = db.Column(db.String(20), nullable=True)
    start_time   = db.Column(db.String(50), nullable=True)