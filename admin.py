from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from database.db import query_db, execute_db, get_db
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Summary KPI Statistics
    total_customers = query_db("SELECT COUNT(*) as count FROM users WHERE role = 'customer'", one=True)['count']
    total_points_issued = query_db("SELECT COALESCE(SUM(points), 0) as total FROM loyalty_transactions WHERE points > 0", one=True)['total']
    total_rewards = query_db("SELECT COUNT(*) as count FROM rewards", one=True)['count']
    active_coupons = query_db("SELECT COUNT(*) as count FROM coupons WHERE status = 'active'", one=True)['count']
    active_campaigns = query_db("SELECT COUNT(*) as count FROM campaigns WHERE status = 'active'", one=True)['count']
    purchase_stats = query_db("SELECT COUNT(*) as count, COALESCE(SUM(final_amount), 0) as revenue FROM purchases", one=True)
    
    # Recent Activities
    recent_customers = query_db("SELECT * FROM users WHERE role = 'customer' ORDER BY created_at DESC LIMIT 5")
    recent_purchases = query_db("""
        SELECT p.*, u.name as customer_name, u.email as customer_email 
        FROM purchases p
        JOIN users u ON p.customer_id = u.id
        ORDER BY p.created_at DESC LIMIT 5
    """)
    recent_redemptions = query_db("""
        SELECT rr.*, u.name as customer_name, r.name as reward_name
        FROM reward_redemptions rr
        JOIN users u ON rr.customer_id = u.id
        JOIN rewards r ON rr.reward_id = r.id
        ORDER BY rr.redemption_date DESC LIMIT 5
    """)
    recent_coupon_usage = query_db("""
        SELECT cu.*, c.code as coupon_code, c.name as coupon_name, u.name as customer_name
        FROM coupon_usage cu
        JOIN coupons c ON cu.coupon_id = c.id
        JOIN users u ON cu.customer_id = u.id
        ORDER BY cu.used_at DESC LIMIT 5
    """)

    return render_template(
        'admin/dashboard.html',
        total_customers=total_customers,
        total_points_issued=total_points_issued,
        total_rewards=total_rewards,
        active_coupons=active_coupons,
        active_campaigns=active_campaigns,
        total_purchases_count=purchase_stats['count'],
        total_revenue=purchase_stats['revenue'],
        recent_customers=recent_customers,
        recent_purchases=recent_purchases,
        recent_redemptions=recent_redemptions,
        recent_coupon_usage=recent_coupon_usage
    )

@admin_bp.route('/customers')
@admin_required
def customers():
    # Fetch all customers with aggregated statistics
    customers_list = query_db("""
        SELECT 
            u.id, u.name, u.email, u.phone, u.points_balance, u.created_at,
            COUNT(DISTINCT p.id) as total_purchases_count,
            COALESCE(SUM(p.final_amount), 0) as total_spent,
            COUNT(DISTINCT rr.id) as total_redemptions
        FROM users u
        LEFT JOIN purchases p ON u.id = p.customer_id
        LEFT JOIN reward_redemptions rr ON u.id = rr.customer_id
        WHERE u.role = 'customer'
        GROUP BY u.id, u.name, u.email, u.phone, u.points_balance, u.created_at
        ORDER BY u.created_at DESC
    """)
    return render_template('admin/customers.html', customers=customers_list)

@admin_bp.route('/customers/add', methods=['POST'])
@admin_required
def add_customer():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip() or 'Customer@123'

    if not name or not email or not phone:
        flash('Name, email, and phone number are required.', 'danger')
        return redirect(url_for('admin.customers'))

    existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
    if existing:
        flash('A customer with this email address already exists.', 'danger')
        return redirect(url_for('admin.customers'))

    hashed_password = generate_password_hash(password)
    try:
        execute_db(
            "INSERT INTO users (name, email, phone, password_hash, role, points_balance) VALUES (%s, %s, %s, %s, 'customer', 0)",
            (name, email, phone, hashed_password)
        )
        flash(f'Customer "{name}" added successfully with default password "{password}".', 'success')
    except Exception as e:
        flash(f'Failed to add customer: {str(e)}', 'danger')

    return redirect(url_for('admin.customers'))

@admin_bp.route('/customers/<int:customer_id>')
@admin_required
def customer_detail(customer_id):
    customer = query_db("SELECT * FROM users WHERE id = %s AND role = 'customer'", (customer_id,), one=True)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('admin.customers'))

    # Calculate Tier
    points_earned = query_db(
        "SELECT COALESCE(SUM(points), 0) as total FROM loyalty_transactions WHERE customer_id = %s AND points > 0",
        (customer_id,),
        one=True
    )['total']
    
    tier = 'Bronze'
    if points_earned >= 1000:
        tier = 'Platinum'
    elif points_earned >= 500:
        tier = 'Gold'
    elif points_earned >= 200:
        tier = 'Silver'

    # Customer Transactions
    transactions = query_db(
        "SELECT * FROM loyalty_transactions WHERE customer_id = %s ORDER BY created_at DESC",
        (customer_id,)
    )
    # Customer Purchases
    purchases = query_db(
        "SELECT p.*, c.code as coupon_code FROM purchases p LEFT JOIN coupons c ON p.coupon_id = c.id WHERE p.customer_id = %s ORDER BY p.purchase_date DESC",
        (customer_id,)
    )
    # Customer Redemptions
    redemptions = query_db(
        """
        SELECT rr.*, r.name as reward_name, r.reward_value
        FROM reward_redemptions rr
        JOIN rewards r ON rr.reward_id = r.id
        WHERE rr.customer_id = %s
        ORDER BY rr.redemption_date DESC
        """,
        (customer_id,)
    )

    return render_template(
        'admin/customer_detail.html',
        customer=customer,
        tier=tier,
        points_earned=points_earned,
        transactions=transactions,
        purchases=purchases,
        redemptions=redemptions
    )

@admin_bp.route('/customers/<int:customer_id>/edit', methods=['POST'])
@admin_required
def edit_customer(customer_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()

    if not name or not email or not phone:
        flash('All fields are required for updating customer profile.', 'danger')
        return redirect(url_for('admin.customer_detail', customer_id=customer_id))

    # Check duplicate email for another user
    existing = query_db("SELECT id FROM users WHERE email = %s AND id != %s", (email, customer_id), one=True)
    if existing:
        flash('Email address is already in use by another customer.', 'danger')
        return redirect(url_for('admin.customer_detail', customer_id=customer_id))

    try:
        execute_db(
            "UPDATE users SET name = %s, email = %s, phone = %s WHERE id = %s",
            (name, email, phone, customer_id)
        )
        flash('Customer profile updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating customer: {str(e)}', 'danger')

    return redirect(url_for('admin.customer_detail', customer_id=customer_id))

@admin_bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@admin_required
def delete_customer(customer_id):
    customer = query_db("SELECT name FROM users WHERE id = %s AND role = 'customer'", (customer_id,), one=True)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('admin.customers'))

    try:
        execute_db("DELETE FROM users WHERE id = %s", (customer_id,))
        flash(f'Customer "{customer["name"]}" deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'danger')

    return redirect(url_for('admin.customers'))

@admin_bp.route('/points/adjust', methods=['POST'])
@admin_required
def adjust_points():
    customer_id = request.form.get('customer_id', type=int)
    points_delta = request.form.get('points', type=int)
    adjustment_type = request.form.get('adjustment_type', 'credit') # credit or debit
    reason = request.form.get('reason', '').strip() or 'Admin Manual Balance Adjustment'

    if not customer_id or not points_delta or points_delta <= 0:
        flash('Please provide a valid customer and non-zero points value.', 'danger')
        return redirect(request.referrer or url_for('admin.customers'))

    customer = query_db("SELECT * FROM users WHERE id = %s AND role = 'customer'", (customer_id,), one=True)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('admin.customers'))

    actual_points = points_delta if adjustment_type == 'credit' else -points_delta

    # Atomic transaction for points adjustment
    with get_db() as db:
        new_balance = customer['points_balance'] + actual_points
        if new_balance < 0:
            flash('Cannot debit more points than the customer currently holds.', 'danger')
            return redirect(url_for('admin.customer_detail', customer_id=customer_id))

        db.execute(
            "UPDATE users SET points_balance = %s WHERE id = %s",
            (new_balance, customer_id)
        )
        db.execute(
            "INSERT INTO loyalty_transactions (customer_id, purchase_id, transaction_type, points, description) VALUES (%s, NULL, 'ADJUSTMENT', %s, %s)",
            (customer_id, actual_points, f"{'Manual Credit' if actual_points > 0 else 'Manual Debit'}: {reason}")
        )

    flash(f"Points successfully adjusted for {customer['name']}. New balance: {new_balance} pts.", 'success')
    return redirect(url_for('admin.customer_detail', customer_id=customer_id))
