from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from routes.routes import api
from routes.web_routes import web
from db.init_db import init_db
from prometheus_flask_exporter import PrometheusMetrics

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

# Ajout de Prometheus
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'LOG430 Flask App', version='4.0')

app.register_blueprint(api)
app.register_blueprint(web)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
