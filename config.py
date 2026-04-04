import os
from dotenv import load_dotenv 
load_dotenv()

# Generate a real secret via: python -c "import secrets; print(secrets.token_hex())"
SECRET_KEY = os.getenv('SECRET_KEY')

# Use DATABASE_URL if provided (Heroku-style), otherwise fall back to local PostgreSQL
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

# Disable the noisy FS event system in dev
SQLALCHEMY_TRACK_MODIFICATIONS = False 