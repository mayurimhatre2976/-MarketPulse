import random
import string
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import query_db, execute_db, get_db
from routes.auth import admin_required, customer_required

rewards_bp = Blueprint('rewards', __name__)

def generate_voucher_code():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"MP-REW-{suffix}"

# ================= ADMIN ROUTES =================

@rewards_bp.route('/admin/rewards')
@admin_required
def list_rewards_admin():
    rewards = query_db("""
        SELECT r.*, COUNT(rr.id) as total_redemptions
        FROM rewards r
        LEFT JOIN reward_redemptions rr ON r.id = rr.reward_id
        GROUP BY r.id, r.name, r.description, r.required_points, r.reward_value, r.stock, r.expiry_date, r.status, r.created_at
        ORDER BY r.created_at DESC
    """)
    return render_template('admin/rewards.html', rewards=rewards, today_date=date.today().strftime('%Y-%m-%d'))

@rewards_bp.route('/admin/rewards/add', methods=['POST'])
@admin_required
def add_reward():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    required_points = request.form.get('required_points', type=int)
    reward_value = request.form.get('reward_value', type=float)
    stock = request.form.get('stock', type=int)
    expiry_date = request.form.get('expiry_date', '').strip()
    status = request.form.get('status', 'active')

    if not name or not required_points or required_points <= 0 or not expiry_date:
        flash('Reward Name, Valid Required Points, and Expiry Date are required.', 'danger')
        return redirect(url_for('rewards.list_rewards_admin'))

    try:
        execute_db(
            """
            INSERT INTO rewards (name, description, required_points, reward_value, stock, expiry_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (name, description, required_points, reward_value or 0.0, stock or 0, expiry_date, status)
        )
        flash(f'Reward "{name}" created successfully.', 'success')
    except Exception as e:
        flash(f'Failed to add reward: {str(e)}', 'danger')

    return redirect(url_for('rewards.list_rewards_admin'))

@rewards_bp.route('/admin/rewards/<int:reward_id>/edit', methods=['POST'])
@admin_required
def edit_reward(reward_id):
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    required_points = request.form.get('required_points', type=int)
    reward_value = request.form.get('reward_value', type=float)
    stock = request.form.get('stock', type=int)
    expiry_date = request.form.get('expiry_date', '').strip()
    status = request.form.get('status', 'active')

    if not name or not required_points or required_points <= 0 or not expiry_date:
        flash('Reward Name, Valid Required Points, and Expiry Date are required.', 'danger')
        return redirect(url_for('rewards.list_rewards_admin'))

    try:
        execute_db(
            """
            UPDATE rewards 
            SET name = %s, description = %s, required_points = %s, reward_value = %s, stock = %s, expiry_date = %s, status = %s
            WHERE id = %s
            """,
            (name, description, required_points, reward_value or 0.0, stock or 0, expiry_date, status, reward_id)
        )
        flash('Reward updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating reward: {str(e)}', 'danger')

    return redirect(url_for('rewards.list_rewards_admin'))

@rewards_bp.route('/admin/rewards/<int:reward_id>/delete', methods=['POST'])
@admin_required
def delete_reward(reward_id):
    # Check if redemptions exist
    redemptions = query_db("SELECT id FROM reward_redemptions WHERE reward_id = %s", (reward_id,))
    if redemptions:
        # Mark inactive instead of deleting to preserve historical records
        execute_db("UPDATE rewards SET status = 'inactive' WHERE id = %s", (reward_id,))
        flash('Reward has existing redemptions and cannot be deleted; marked as Inactive instead.', 'warning')
    else:
        execute_db("DELETE FROM rewards WHERE id = %s", (reward_id,))
        flash('Reward deleted successfully.', 'success')

    return redirect(url_for('rewards.list_rewards_admin'))

@rewards_bp.route('/admin/rewards/redemptions')
@admin_required
def list_redemptions_admin():
    redemptions = query_db("""
        SELECT rr.*, u.name as customer_name, u.email as customer_email, r.name as reward_name, r.reward_value
        FROM reward_redemptions rr
        JOIN users u ON rr.customer_id = u.id
        JOIN rewards r ON rr.reward_id = r.id
        ORDER BY rr.redemption_date DESC
    """)
    return render_template('admin/redemptions.html', redemptions=redemptions)


# ================= CUSTOMER ROUTES =================

@rewards_bp.route('/customer/rewards')
@customer_required
def list_rewards_customer():
    user_id = session.get('user_id')
    customer = query_db("SELECT points_balance FROM users WHERE id = %s", (user_id,), one=True)
    today_str = date.today().strftime('%Y-%m-%d')
    
    # Available active rewards
    rewards = query_db("""
        SELECT * FROM rewards 
        WHERE status = 'active' AND expiry_date >= %s 
        ORDER BY required_points ASC
    """, (today_str,))

    return render_template(
        'customer/rewards.html',
        rewards=rewards,
        points_balance=customer['points_balance'] if customer else 0
    )

@rewards_bp.route('/customer/rewards/redeem/<int:reward_id>', methods=['POST'])
@customer_required
def redeem_reward(reward_id):
    user_id = session.get('user_id')
    today_str = date.today().strftime('%Y-%m-%d')

    reward = query_db("SELECT * FROM rewards WHERE id = %s", (reward_id,), one=True)
    if not reward:
        flash('Reward not found.', 'danger')
        return redirect(url_for('rewards.list_rewards_customer'))

    if reward['status'] != 'active':
        flash('This reward is currently not active.', 'danger')
        return redirect(url_for('rewards.list_rewards_customer'))

    if str(reward['expiry_date']) < today_str:
        flash('This reward has expired.', 'danger')
        return redirect(url_for('rewards.list_rewards_customer'))

    if reward['stock'] <= 0:
        flash('Sorry, this reward is out of stock.', 'danger')
        return redirect(url_for('rewards.list_rewards_customer'))

    customer = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if not customer or customer['points_balance'] < reward['required_points']:
        flash(f"Insufficient loyalty points. You need {reward['required_points']} pts (You have {customer['points_balance'] if customer else 0} pts).", 'danger')
        return redirect(url_for('rewards.list_rewards_customer'))

    voucher_code = generate_voucher_code()

    # Atomic redemption transaction
    with get_db() as db:
        # Deduct customer points
        new_balance = customer['points_balance'] - reward['required_points']
        db.execute("UPDATE users SET points_balance = %s WHERE id = %s", (new_balance, user_id))

        # Decrement reward stock
        db.execute("UPDATE rewards SET stock = stock - 1 WHERE id = %s", (reward_id,))

        # Record redemption
        db.execute(
            """
            INSERT INTO reward_redemptions (customer_id, reward_id, points_used, redemption_code, status)
            VALUES (%s, %s, %s, %s, 'completed')
            """,
            (user_id, reward_id, reward['required_points'], voucher_code)
        )

        # Log points transaction ledger
        db.execute(
            """
            INSERT INTO loyalty_transactions (customer_id, purchase_id, transaction_type, points, description)
            VALUES (%s, NULL, 'REDEEM', %s, %s)
            """,
            (user_id, -reward['required_points'], f"Redeemed {reward['name']} (Voucher: {voucher_code})")
        )

    flash(f"🎉 Congratulations! You have successfully redeemed '{reward['name']}'. Your voucher code is {voucher_code}.", 'success')
    return redirect(url_for('rewards.my_redemptions'))

@rewards_bp.route('/customer/rewards/my-redemptions')
@customer_required
def my_redemptions():
    user_id = session.get('user_id')
    redemptions = query_db("""
        SELECT rr.*, r.name as reward_name, r.description as reward_description, r.reward_value, r.expiry_date
        FROM reward_redemptions rr
        JOIN rewards r ON rr.reward_id = r.id
        WHERE rr.customer_id = %s
        ORDER BY rr.redemption_date DESC
    """, (user_id,))

    return render_template('customer/my_redemptions.html', redemptions=redemptions)
