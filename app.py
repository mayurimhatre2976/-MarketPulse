import os
from flask import Flask, render_template, session
from config import Config
from database.db import query_db, init_database_tables

# Import Route Blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.customer import customer_bp
from routes.purchases import purchases_bp
from routes.rewards import rewards_bp
from routes.coupons import coupons_bp
from routes.campaigns import campaigns_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database tables if not created
    with app.app_context():
        try:
            init_database_tables()
        except Exception as e:
            print(f"[NOTE] Database auto-init check: {e}")

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(coupons_bp)
    app.register_blueprint(campaigns_bp)

    # Custom Jinja Template Filters
    @app.template_filter('currency')
    def format_currency(value):
        try:
            val = float(value)
            return f"{Config.CURRENCY_SYMBOL}{val:,.2f}"
        except (ValueError, TypeError):
            return f"{Config.CURRENCY_SYMBOL}0.00"

    # Global Template Context Processor
    @app.context_processor
    def inject_global_vars():
        user_points = 0
        user_role = session.get('role')
        user_id = session.get('user_id')

        if user_id and user_role == 'customer':
            cust = query_db("SELECT points_balance FROM users WHERE id = %s", (user_id,), one=True)
            if cust:
                user_points = cust['points_balance']

        return {
            'currency_symbol': Config.CURRENCY_SYMBOL,
            'current_user_points': user_points
        }

    # Main Landing Page Route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Custom HTTP Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Run locally on port 5000 with debug enabled for development
    app.run(host='0.0.0.0', port=5000, debug=True)
