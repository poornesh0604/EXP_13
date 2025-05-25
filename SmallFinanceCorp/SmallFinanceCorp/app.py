import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the MySQL database
database_url = os.environ.get("DATABASE_URL", "mysql+pymysql://root:password@localhost/small_finance_corp")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure they're registered
    import models
    
    # Import routes
    import routes
    
    # Create tables if they don't exist (though they should exist from the SQL file)
    try:
        db.create_all()
        logging.info("Database tables verified/created successfully")
    except Exception as e:
        logging.error(f"Database initialization error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
