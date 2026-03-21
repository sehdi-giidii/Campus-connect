# app.py
from flask import Flask, send_from_directory
from flask_cors import CORS
from extensions import db, bcrypt, login_manager
from models.order import Order

def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)

    app.config['SECRET_KEY']                     = 'campusconnect-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///campus.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from models.user import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        db.create_all()
        print("✅ Database tables created!")

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route('/')
    def home():
        return send_from_directory('.', 'Homepage.html')

    @app.route('/student/<path:filename>')
    def student_pages(filename):
        return send_from_directory('static/student', filename)

    @app.route('/provider/<path:filename>')
    def provider_pages(filename):
        return send_from_directory('static/provider', filename)

    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)

    @app.route('/canteen-provider')
    def canteen_provider():
        return send_from_directory('static/provider', 'canteen_provider.html')

    @app.route('/student/store')
    def student_store():
        return send_from_directory('static/student', 'store.html')

    @app.route('/provider/store')
    def provider_store():
        return send_from_directory('static/provider', 'store_provider.html')

    @app.route('/student/scooty')
    def student_scooty():
        return send_from_directory('static/student', 'scooty.html')

    @app.route('/provider/scooty')
    def provider_scooty():
        return send_from_directory('static/provider', 'scooty_provider.html')

    @app.route('/student/my-orders')
    def my_orders_page():
        return send_from_directory('static/student', 'my_orders.html')

    @app.route('/provider/hospital')
    def hospital_provider():
        return send_from_directory('static/provider', 'hospital_provider.html')

    @app.route('/provider/postoffice')
    def postoffice_provider():
        return send_from_directory('static/provider', 'postoffice_provider.html')

    @app.route('/provider/bus')
    def bus_provider():
        return send_from_directory('static/provider', 'bus_provider.html')

    @app.route('/student/hospital')
    def hospital_page():
        return send_from_directory('static/student', 'hospital.html')

    @app.route('/student/postoffice')
    def postoffice_page():
        return send_from_directory('static/student', 'postoffice.html')

    @app.route('/student/bus')
    def bus_page():
        return send_from_directory('static/student', 'bus.html')

    return app

# This is used by gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)