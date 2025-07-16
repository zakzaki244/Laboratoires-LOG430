from flask import Flask
from config import Config
from infrastructure.db import db
from interface.checkout_routes import bp as checkout_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(checkout_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)