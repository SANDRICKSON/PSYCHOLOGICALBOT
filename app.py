from flask import Flask, render_template, url_for, request, jsonify, redirect, flash, session
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from forms import RegisterForm
from extensions import app
from werkzeug.utils import secure_filename
import os

# Rasa REST API URL (Make sure your Rasa server is running and accessible)
RASA_LINK = "http://127.0.0.1:5005"
RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'

DATABASE = 'instance/database.db'  # Ensure it points to 'database.db' in the instance folder

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Define the login route

def get_db():
    conn = sqlite3.connect(DATABASE)  # This connects to the 'instance/database.db'
    return conn

class User(UserMixin):
    # This class is used to represent the logged-in user.
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# Load user by user_id
@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    return None

# Create 'users' table if it doesn't exist
def create_users_table():
    conn = get_db()
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL,
                        birthday TEXT,
                        country TEXT,
                        gender TEXT,
                        profile_image TEXT)''')
    conn.commit()
    conn.close()

# Call the table creation function to ensure the table is created on app startup
create_users_table()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))  # If the user is already logged in, redirect them to home page

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        birthday = form.birthday.data
        country = form.country.data
        gender = form.gender.data

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))

        # Hash the password before saving
        hashed_password = generate_password_hash(password)

        # Insert data into database
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password, birthday, country, gender) VALUES (?, ?, ?, ?, ?, ?)",
                           (username, email, hashed_password, birthday, country, gender))
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            # Redirect to login with pre-filled username
            return redirect(url_for("login", username=username))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for('register'))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))  # If the user is already logged in, redirect them to home page

    username = request.args.get('username')  # Retrieve the username from the query parameters

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):  # Assuming the password is the 4th column
            user_obj = User(id=user[0], username=user[1], email=user[2])
            login_user(user_obj)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html", username=username)  # Pre-fill the username field

@app.route("/logout")
@login_required
def logout():
    logout_user()  # Log out the current user
    flash("You have been logged out", "success")
    return redirect(url_for("home"))  # Redirect to login page after logout

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/chatbot")
@login_required
def chatbot():
    # Chatbot's predefined texts
    chat_texts = [
        "Hello how are you?",
        "I'm fine thank you and you?",
        "Doing good, thanks",
    ]
    return render_template("chatbot.html", texts=chat_texts)

# New route for handling chatbot messages and integrating with Rasa
@app.route("/send_message", methods=['POST'])
@login_required
def send_message():
    if request.is_json:
        user_message = request.get_json().get('message')
    else:
        return jsonify({"error": "Invalid JSON format"}), 400

    if user_message:
        # Send the message to Rasa API with user message
        payload = {"message": user_message}
        response = requests.post(RASA_API_URL, json=payload)

        if response.status_code == 200:
            # Get the response from Rasa
            rasa_response = response.json()

            # If Rasa responded, return the response; otherwise, return a default message
            if rasa_response:
                bot_message = rasa_response[0].get('text', "Sorry, I didn't understand that.")
            else:
                bot_message = "Sorry, I didn't understand that."
        else:
            bot_message = "Error with Rasa server."

        return jsonify({"response": bot_message})
    else:
        return jsonify({"error": "No message provided"}), 400

# Configure the upload folder for profile images
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if 'profile_image' not in request.files:
            flash("No file part", "danger")
            return redirect(url_for('profile'))

        file = request.files['profile_image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Save the file path in the user's profile (e.g., to a database or session)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?", (filepath, current_user.id))
            conn.commit()
            conn.close()
            flash("Profile image uploaded successfully!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Invalid file format. Only PNG, JPG, JPEG, GIF are allowed.", "danger")
            return redirect(url_for('profile'))

    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True)
