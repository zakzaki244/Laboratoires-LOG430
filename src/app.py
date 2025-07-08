from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from routes.routes import api
from routes.web_routes import web
from db.init_db import init_db

app = Flask(__name__)
CORS(app)
app.secret_key = "secret"
init_db()

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
