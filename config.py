import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'library-dbms-super-secret-key-2026')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')

    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'library_db')

    # SQLite Fallback Path (stored inside database directory)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database', 'library_local.sqlite')
    
    # Overdue fine rate per day (in currency units, e.g. USD / INR)
    DAILY_FINE_RATE = float(os.getenv('DAILY_FINE_RATE', 2.00))
    DEFAULT_LOAN_DAYS = int(os.getenv('DEFAULT_LOAN_DAYS', 14))
