from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api.config import Config
from flask_cors import CORS

# app = Flask(__name__, static_folder="../images", static_url_path="/")
app = Flask(__name__, static_folder="../images")
# app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)

db = SQLAlchemy(app)

from api import routes, models