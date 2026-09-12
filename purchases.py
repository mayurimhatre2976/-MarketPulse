import random
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from database.db import query_db, get_db
from routes.auth import admin_required

purchases_bp = Blueprint('purchases', __name__)

def calculate_points(amount):
    """Calculate points earned for a purchase amount based on backend configuration."""
    if amount <= 0:
        return 0
    return int(amount * Config.POINTS_RATE)

@purchases_bp.route('/admin/purchases')
@admin_required
def list_purchases():
    purchases = query_db("""
        SELECT p.*, u.name as customer_name, u.email as customer_email, c.code as coupon_code
        FROM purchases p
        JOIN users u ON p.customer_id = u.id
        LEFT JOIN coupons c ON p.coupon_id = c.id
        ORDER BY p.purchase_date DESC, p.created_at DESC
    """)
    customers = query_db("SELECT id, name, email, phone FROM users WHERE role = 'customer' ORDER BY name ASC")
    active_coupons = query_db("SELECT * FROM coupons WHERE status = 'active' AND expiry_date >= CURDATE() ORDER BY code ASC")
    
    # Auto-generate a fresh invoice number suggestion
    suggested_invoice = f"INV-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"

    return render_template(
        'admin/purchases.html',
        purchases=purchases,
        customers=customers,
        active_coupons=active_coupons,
        suggested_invoice=suggested_invoice,
        today_date=date.today().strftime('%Y-%m-%d')
    )

@purchases_bp.route('/admin/purchases/new', methods=['POST'])
@admin_required
def create_purchase():
    customer_id = request.form.get('customer_id', type=int)
    invoice_number = request.form.get('invoice_number', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    purchase_date = request.form.get('purchase_date', '').strip() or date.today().strftime('%Y-%m-%d')
    coupon_code = request.form.get('coupon_code', '').strip().upper()
    description = request.form.get('description', '').strip()

    # Validations
    if not customer_id:
        flash('Please select a customer for this purchase.', 'danger')
        return redirect(url_for('purchases.list_purchases'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        flash('Purchase amount must be a positive number.', 'danger')
        return redirect(url_for('purchases.list_purchases'))

    if not invoice_number:
        invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"

    # Check invoice uniqueness
    existing_inv = query_db("SELECT id FROM purchases WHERE invoice_number = %s", (invoice_number,), one=True)
    if existing_inv:
        flash(f'Invoice number "{invoice_number}" already exists. Please use a unique invoice number.', 'danger')
        return redirect(url_for('purchases.list_purchases'))

    customer = query_db("SELECT id, name, points_balance FROM users WHERE id = %s AND role = 'customer'", (customer_id,), one=True)
    if not customer:
        flash('Selected customer does not exist.', 'danger')
        return redirect(url_for('purchases.list_purchases'))

    # Process Coupon Validation if entered
    coupon_id = None
    discount_amount = 0.00
    today_str = date.today().strftime('%Y-%m-%d')

    if coupon_code:
        coupon = query_db("SELECT * FROM coupons WHERE code = %s", (coupon_code,), one=True)
        if not coupon:
            flash(f'Coupon code "{coupon_code}" is invalid.', 'danger')
            return redirect(url_for('purchases.list_purchases'))

        if coupon['status'] != 'active':
            flash(f'Coupon "{coupon_code}" is inactive.', 'danger')
            return redirect(url_for('purchases.list_purchases'))

        if str(coupon['start_date']) > today_str:
            flash(f'Coupon "{coupon_code}" is not valid yet (starts on {coupon["start_date"]}).', 'danger')
            return redirect(url_for('purchases.list_purchases'))

        if str(coupon['expiry_date']) < today_str:
            flash(f'Coupon "{coupon_code}" has expired on {coupon["expiry_date"]}.', 'danger')
            return redirect(url_for('purchases.list_purchases'))

        if coupon['used_count'] >= coupon['maximum_usage']:
            flash(f'Coupon "{coupon_code}" has reached its maximum usage limit.', 'danger')
            return redirect(url_for('purchases.list_purchases'))

        if amount < float(coupon['minimum_purchase']):
            flash(f'Minimum purchase amount of {Config.CURRENCY_SYMBOL}{coupon["minimum_purchase"]} required for coupon "{coupon_code}".', 'danger')
            return redirect(url_for('purchases.list_purchases'))

        # Calculate discount
        if coupon['discount_type'] == 'percentage':
            discount_amount = round((float(coupon['discount_value']) / 100.0) * amount, 2)
        else:
            discount_amount = min(float(coupon['discount_value']), amount)

        coupon_id = coupon['id']

    final_amount = max(0.00, round(amount - discount_amount, 2))
    points_earned = calculate_points(final_amount)

    # Atomic multi-table transaction
    with get_db() as db:
        # 1. Insert Purchase
        db.execute(
            """
            INSERT INTO purchases 
            (customer_id, invoice_number, amount, discount_amount, final_amount, coupon_id, description, purchase_date, points_earned)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (customer_id, invoice_number, amount, discount_amount, final_amount, coupon_id, description, purchase_date, points_earned)
        )
        purchase_id = db.lastrowid

        # 2. Update Customer Points Balance
        new_balance = customer['points_balance'] + points_earned
        db.execute("UPDATE users SET points_balance = %s WHERE id = %s", (new_balance, customer_id))

        # 3. Create Points Transaction Record
        db.execute(
            """
            INSERT INTO loyalty_transactions 
            (customer_id, purchase_id, transaction_type, points, description)
            VALUES (%s, %s, 'EARN', %s, %s)
            """,
            (customer_id, purchase_id, points_earned, f"Points earned on Invoice #{invoice_number}")
        )

        # 4. Record Coupon Usage if coupon was applied
        if coupon_id:
            db.execute(
                """
                INSERT INTO coupon_usage (coupon_id, customer_id, purchase_id, discount_applied)
                VALUES (%s, %s, %s, %s)
                """,
                (coupon_id, customer_id, purchase_id, discount_amount)
            )
            db.execute("UPDATE coupons SET used_count = used_count + 1 WHERE id = %s", (coupon_id,))

    flash(
        f"Purchase recorded successfully! Invoice #{invoice_number} for {customer['name']} earned {points_earned} loyalty points.",
        'success'
    )
    return redirect(url_for('purchases.list_purchases'))

@purchases_bp.route('/api/validate-coupon', methods=['POST'])
def validate_coupon_api():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        amount = 0.0

    if not code:
        return jsonify({'valid': False, 'message': 'Coupon code is required.'})

    coupon = query_db("SELECT * FROM coupons WHERE code = %s", (code,), one=True)
    if not coupon:
        return jsonify({'valid': False, 'message': 'Invalid coupon code.'})

    today_str = date.today().strftime('%Y-%m-%d')
    if coupon['status'] != 'active':
        return jsonify({'valid': False, 'message': 'This coupon is currently inactive.'})

    if str(coupon['start_date']) > today_str:
        return jsonify({'valid': False, 'message': f'Coupon valid from {coupon["start_date"]}.'})

    if str(coupon['expiry_date']) < today_str:
        return jsonify({'valid': False, 'message': f'Coupon expired on {coupon["expiry_date"]}.'})

    if coupon['used_count'] >= coupon['maximum_usage']:
        return jsonify({'valid': False, 'message': 'Coupon usage limit has been reached.'})

    min_purchase = float(coupon['minimum_purchase'])
    if amount < min_purchase:
        return jsonify({
            'valid': False,
            'message': f'Minimum cart total of {Config.CURRENCY_SYMBOL}{min_purchase:.2f} required.'
        })

    if coupon['discount_type'] == 'percentage':
        discount = round((float(coupon['discount_value']) / 100.0) * amount, 2)
        desc = f"{coupon['discount_value']}% Off"
    else:
        discount = min(float(coupon['discount_value']), amount)
        desc = f"{Config.CURRENCY_SYMBOL}{coupon['discount_value']:.2f} Off"

    final_amt = max(0.00, round(amount - discount, 2))
    points_estimate = calculate_points(final_amt)

    return jsonify({
        'valid': True,
        'coupon_id': coupon['id'],
        'code': coupon['code'],
        'name': coupon['name'],
        'discount_type': coupon['discount_type'],
        'discount_value': float(coupon['discount_value']),
        'discount_amount': discount,
        'final_amount': final_amt,
        'estimated_points': points_estimate,
        'message': f"Coupon applied: {desc} (You save {Config.CURRENCY_SYMBOL}{discount:.2f})"
    })
