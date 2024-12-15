from logging import debug
from flask import Flask, render_template, url_for, request, jsonify
import requests
from forms import RegisterForm
from extensions import app

# Rasa REST API URL (Make sure your Rasa server is running and accessible)
RASA_LINK = "http://127.0.0.1:5005"
RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.username.data, form.password.data)
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", method="POST")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/chatbot")
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


if __name__ == "__main__":
    app.run(debug=True)
