from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db
from routes.auth import customer_required

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

def get_tier_info(total_earned):
    """Calculates customer loyalty tier and next tier progress."""
    if total_earned >= 1000:
        return {'name': 'Platinum', 'color': 'purple', 'next_tier': None, 'points_needed': 0, 'progress': 100}
    elif total_earned >= 500:
        return {'name': 'Gold', 'color': 'warning', 'next_tier': 'Platinum', 'points_needed': 1000 - total_earned, 'progress': int((total_earned / 1000) * 100)}
    elif total_earned >= 200:
        return {'name': 'Silver', 'color': 'secondary', 'next_tier': 'Gold', 'points_needed': 500 - total_earned, 'progress': int((total_earned / 500) * 100)}
    else:
        return {'name': 'Bronze', 'color': 'amber', 'next_tier': 'Silver', 'points_needed': 200 - total_earned, 'progress': int((total_earned / 200) * 100)}

@customer_bp.route('/dashboard')
@customer_required
def dashboard():
    user_id = session.get('user_id')
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Aggregate Points Stats
    total_earned = query_db(
        "SELECT COALESCE(SUM(points), 0) as total FROM loyalty_transactions WHERE customer_id = %s AND points > 0",
        (user_id,),
        one=True
    )['total']

    total_redeemed = query_db(
        "SELECT COALESCE(ABS(SUM(points)), 0) as total FROM loyalty_transactions WHERE customer_id = %s AND transaction_type = 'REDEEM'",
        (user_id,),
        one=True
    )['total']

    rewards_count = query_db(
        "SELECT COUNT(*) as count FROM reward_redemptions WHERE customer_id = %s",
        (user_id,),
        one=True
    )['count']

    tier_info = get_tier_info(total_earned)

    # Recent Activity
    recent_purchases = query_db(
        "SELECT p.*, c.code as coupon_code FROM purchases p LEFT JOIN coupons c ON p.coupon_id = c.id WHERE p.customer_id = %s ORDER BY p.purchase_date DESC LIMIT 3",
        (user_id,)
    )

    recent_transactions = query_db(
        "SELECT * FROM loyalty_transactions WHERE customer_id = %s ORDER BY created_at DESC LIMIT 5",
        (user_id,)
    )

    recent_redemptions = query_db(
        """
        SELECT rr.*, r.name as reward_name, r.reward_value
        FROM reward_redemptions rr
        JOIN rewards r ON rr.reward_id = r.id
        WHERE rr.customer_id = %s
        ORDER BY rr.redemption_date DESC LIMIT 3
        """,
        (user_id,)
    )

    # Active Campaigns preview
    active_campaigns = query_db(
        "SELECT * FROM campaigns WHERE status = 'active' AND start_date <= CURDATE() AND end_date >= CURDATE() ORDER BY end_date ASC LIMIT 2"
    )

    return render_template(
        'customer/dashboard.html',
        user=user,
        current_points=user['points_balance'],
        total_earned=total_earned,
        total_redeemed=total_redeemed,
        rewards_count=rewards_count,
        tier_info=tier_info,
        recent_purchases=recent_purchases,
        recent_transactions=recent_transactions,
        recent_redemptions=recent_redemptions,
        active_campaigns=active_campaigns
    )

@customer_bp.route('/points')
@customer_required
def points_history():
    user_id = session.get('user_id')
    user = query_db("SELECT points_balance FROM users WHERE id = %s", (user_id,), one=True)
    transactions = query_db(
        "SELECT * FROM loyalty_transactions WHERE customer_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    total_earned = query_db(
        "SELECT COALESCE(SUM(points), 0) as total FROM loyalty_transactions WHERE customer_id = %s AND points > 0",
        (user_id,),
        one=True
    )['total']
    total_redeemed = query_db(
        "SELECT COALESCE(ABS(SUM(points)), 0) as total FROM loyalty_transactions WHERE customer_id = %s AND transaction_type = 'REDEEM'",
        (user_id,),
        one=True
    )['total']

    return render_template(
        'customer/points.html',
        transactions=transactions,
        current_points=user['points_balance'] if user else 0,
        total_earned=total_earned,
        total_redeemed=total_redeemed
    )

@customer_bp.route('/purchases')
@customer_required
def purchase_history():
    user_id = session.get('user_id')
    purchases = query_db(
        """
        SELECT p.*, c.code as coupon_code, c.name as coupon_name
        FROM purchases p
        LEFT JOIN coupons c ON p.coupon_id = c.id
        WHERE p.customer_id = %s
        ORDER BY p.purchase_date DESC
        """,
        (user_id,)
    )
    total_spent = query_db("SELECT COALESCE(SUM(final_amount), 0) as total FROM purchases WHERE customer_id = %s", (user_id,), one=True)['total']

    return render_template('customer/purchases.html', purchases=purchases, total_spent=total_spent)

@customer_bp.route('/profile', methods=['GET', 'POST'])
@customer_required
def profile():
    user_id = session.get('user_id')
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            phone = request.form.get('phone', '').strip()
            name = request.form.get('name', '').strip()

            if not name or not phone:
                flash('Name and phone number cannot be empty.', 'danger')
                return redirect(url_for('customer.profile'))

            execute_db("UPDATE users SET name = %s, phone = %s WHERE id = %s", (name, phone, user_id))
            session['name'] = name
            flash('Profile details updated successfully.', 'success')
            return redirect(url_for('customer.profile'))

        elif action == 'change_password':
            current_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')

            if not check_password_hash(user['password_hash'], current_pwd):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('customer.profile'))

            if len(new_pwd) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return redirect(url_for('customer.profile'))

            if new_pwd != confirm_pwd:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('customer.profile'))

            new_hash = generate_password_hash(new_pwd)
            execute_db("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
            flash('Password changed successfully.', 'success')
            return redirect(url_for('customer.profile'))

    total_earned = query_db("SELECT COALESCE(SUM(points), 0) as total FROM loyalty_transactions WHERE customer_id = %s AND points > 0", (user_id,), one=True)['total']
    tier_info = get_tier_info(total_earned)

    return render_template('customer/profile.html', user=user, tier_info=tier_info, total_earned=total_earned)
