from flask import Flask
from flask_mail import Mail
from config import Config
from extensions import db, mail
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.admin import admin_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    print(f"500 Error: {error}")
    import traceback
    traceback.print_exc()
    return {'error': 'Internal server error', 'details': str(error)}, 500

@app.errorhandler(404)
def not_found_error(error):
    return {'error': 'Not found'}, 404

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully")

@app.route('/')
def landing():
    from flask import render_template
    return render_template('landing.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
