from flask import Flask
import cloudinary
import cloudinary.uploader
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv('DB_NAME')  # Get the DB name from environment variable
DB_USERNAME = os.getenv('DB_USERNAME')  # Get DB username from environment variable
DB_PASSWORD = os.getenv('DB_PASSWORD')  # Get DB password from environment variable
DB_HOST = os.getenv('DB_HOST')  # Get DB host from environment variable

CLOUD_NAME = os.getenv('CLOUD_NAME')  # Get Cloudinary Cloud Name
API_KEY = os.getenv('API_KEY')  # Get Cloudinary API Key
API_SECRET = os.getenv('API_SECRET')  # Get Cloudinary API Secret
SECRET_KEY = os.getenv('SECRET_KEY')  # Get Flask secret key

# Initialize MySQL
mysql = MySQL()    

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET
    )

    # Configure MySQL
    app.config['MYSQL_HOST'] = DB_HOST
    app.config['MYSQL_USER'] = DB_USERNAME
    app.config['MYSQL_PASSWORD'] = DB_PASSWORD
    app.config['MYSQL_DB'] = DB_NAME

    # Initialize MySQL with the app
    mysql.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix="/")

    return app, mysql
