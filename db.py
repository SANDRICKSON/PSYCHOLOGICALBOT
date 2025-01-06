from extensions import app, db
from models import User

# Create all tables if not already created
from extensions import init_db
init_db()

# Querying all users (for example purposes)
with app.app_context():
    users = User.query.all()  # This retrieves all users from the database
    for user in users:
        print(f"User: {user.username}")
