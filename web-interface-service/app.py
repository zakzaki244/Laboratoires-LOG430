from flask import Flask, redirect, url_for
from config import Config
from routes.web_routes import bp as web_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(web_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('web.login'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)