from flask import Flask
from routes.customers import customers_bp
from routes.tickets import tickets_bp
from routes.dashboard import dashboard_bp
from routes.users import users_bp
from routes.auth import auth_bp

app = Flask(__name__)

app.register_blueprint(customers_bp, url_prefix='/customers')
app.register_blueprint(tickets_bp, url_prefix='/tickets')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route("/")
def home():
    return {'message' : 'Smart Desk API is working!'}


if __name__ == "__main__":
    app.run(debug=True)
