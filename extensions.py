from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "sandrikela1$"  # Replace with a strong secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"  # Your SQLite URI

db = SQLAlchemy(app)  # Make sure the db instance is associated with the app

# Optionally, if you want to create tables on app startup, do it in the main file or after app initialization.
def init_db():
    with app.app_context():
        db.create_all()  # Automatically creates the tables if they do not exist
