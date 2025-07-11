from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from routes.routes import api
from routes.web_routes import web
from db.init_db import init_db
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app.extensions import cache


app = Flask(__name__)
CORS(app)
app.secret_key = "secret"


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "A swagger API",
        "version": "0.0.1"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Token d'authentification"
        }
    },
    "security": [{"Bearer": []}]
}
swagger = Swagger(app, template=swagger_template)

app.register_blueprint(api)
app.register_blueprint(web)

# Ajout de Prometheus
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'LOG430 Flask App', version='4.0')

# Ajout manuellement /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


cache.init_app(app)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
