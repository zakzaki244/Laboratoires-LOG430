from flask import Flask
from config import Config
from routes.gateway_routes import bp as gateway_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(Config)
    app.register_blueprint(gateway_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080)