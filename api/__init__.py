from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from api.config import Config
from flask_cors import CORS
from flask_login import LoginManager


# app = Flask(__name__, static_folder="../images", static_url_path="/")
app = Flask(__name__, static_folder="../images")
# app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)

# Setting cross origin policy
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Database
db = SQLAlchemy(app)

# Initialize Bcrypt
bcrypt = Bcrypt()

from api import routes, models