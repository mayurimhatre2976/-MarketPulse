import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'marketpulse-super-secret-key-2026')
    
    # Database Configuration (Default XAMPP MySQL Settings)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'marketpulse')
    
    # Loyalty Points Rule Configuration
    # Example: 10 loyalty points for every ₹100 spent (0.1 points per currency unit)
    POINTS_PER_100_SPENT = float(os.environ.get('POINTS_PER_100_SPENT', 10.0))
    POINTS_RATE = POINTS_PER_100_SPENT / 100.0  # 0.10
    
    # Currency Symbol
    CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '₹')
    
    # Session Lifetime
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
