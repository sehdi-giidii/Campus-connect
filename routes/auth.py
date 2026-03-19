# routes/auth.py
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from extensions import db, bcrypt
from models.user import User
import json
from datetime import datetime
from flask_login import current_user
from models.order import Order

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/student/signup', methods=['POST'])
def student_signup():
    data     = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    roll     = data.get('roll', '').strip()
    password = data.get('password', '')

    if not name or not email or not roll or not password:
        return jsonify({'error': 'All fields are required.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'This email is already registered.'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user  = User(name=name, email=email, password=hashed_pw, role='student', roll_no=roll)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Account created successfully!'}), 201

@auth_bp.route('/api/student/login', methods=['POST'])
def student_login():
    data     = request.get_json()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'All fields are required.'}), 400

    user = User.query.filter_by(email=email, role='student').first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    login_user(user)
    return jsonify({'message': 'Login successful!', 'name': user.name}), 200

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200

# ── PROVIDER SIGNUP ──
@auth_bp.route('/api/provider/signup', methods=['POST'])
def provider_signup():
    from models.user import User
    data     = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')
    service  = data.get('service', '')

    if not name or not email or not password or not service:
        return jsonify({'error': 'All fields are required.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'This email is already registered.'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user  = User(name=name, email=email, password=hashed_pw, role='provider', service=service)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Provider registered successfully!'}), 201


# ── PROVIDER LOGIN ──
@auth_bp.route('/api/provider/login', methods=['POST'])
def provider_login():
    from models.user import User
    data     = request.get_json()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'All fields are required.'}), 400

    user = User.query.filter_by(email=email, role='provider').first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    login_user(user)
    return jsonify({'message': 'Login successful!', 'name': user.name, 'service': user.service}), 200

@auth_bp.route('/api/place-order', methods=['POST'])
@login_required
def place_order():
    data    = request.get_json()
    service = data.get('service')
    items   = data.get('items', [])
    total   = data.get('total', 0)
    ref     = service[0].upper() + 'C' + str(int(datetime.utcnow().timestamp()))[-6:]
    order   = Order(
        order_ref = ref,
        user_id   = current_user.id,
        service   = service,
        items     = json.dumps(items),
        total     = total,
        status    = 'completed'
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order placed!', 'order_ref': ref}), 201


@auth_bp.route('/api/place-scooty', methods=['POST'])
@login_required
def place_scooty():
    data  = request.get_json()
    ref   = 'SR' + str(int(datetime.utcnow().timestamp()))[-6:]
    order = Order(
        order_ref    = ref,
        user_id      = current_user.id,
        service      = 'scooty',
        items        = json.dumps([]),
        total        = data.get('total', 0),
        status       = 'active',
        scooty_id    = data.get('scootyId'),
        scooty_model = data.get('model'),
        rental_type  = data.get('rentalType'),
        duration     = data.get('duration'),
        start_time   = data.get('start'),
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Booking confirmed!', 'order_ref': ref}), 201


@auth_bp.route('/api/my-orders', methods=['GET'])
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()

    canteen, store, scooty = [], [], []
    for o in orders:
        base = {
            'id':     o.order_ref,
            'time':   o.created_at.strftime('%d %b, %I:%M %p'),
            'status': o.status,
        }
        if o.service == 'canteen':
            base['items'] = json.loads(o.items)
            canteen.append(base)
        elif o.service == 'store':
            base['items'] = json.loads(o.items)
            store.append(base)
        elif o.service == 'scooty':
            base['total']      = o.total
            base['scootyId']   = o.scooty_id
            base['model']      = o.scooty_model
            base['rentalType'] = o.rental_type
            base['duration']   = o.duration
            base['start']      = o.start_time
            scooty.append(base)

    return jsonify({'canteen': canteen, 'store': store, 'scooty': scooty}), 200