import os 
import json

# Get the json config path
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'config.json')

# Load config.json
with open(filepath) as config_file:
    config = json.load(config_file)

class Config():
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = config.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    #CONFIGURATION D'UN COMPTE MAIL DANS NOTRE APP !
    # MAIL_SERVER = 'smtp.googlemail.com' # smtp.gmail.com ?
    # MAIL_PORT = 587 # 465 ?
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')