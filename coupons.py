from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import query_db, execute_db
from routes.auth import admin_required, customer_required

coupons_bp = Blueprint('coupons', __name__)

# ================= ADMIN ROUTES =================

@coupons_bp.route('/admin/coupons')
@admin_required
def list_coupons_admin():
    coupons = query_db("""
        SELECT c.*, COUNT(cu.id) as actual_usage_count
        FROM coupons c
        LEFT JOIN coupon_usage cu ON c.id = cu.coupon_id
        GROUP BY c.id, c.code, c.name, c.description, c.discount_type, c.discount_value, c.minimum_purchase, c.maximum_usage, c.used_count, c.start_date, c.expiry_date, c.status, c.created_at
        ORDER BY c.created_at DESC
    """)
    return render_template('admin/coupons.html', coupons=coupons, today_date=date.today().strftime('%Y-%m-%d'))

@coupons_bp.route('/admin/coupons/add', methods=['POST'])
@admin_required
def add_coupon():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    discount_type = request.form.get('discount_type', 'fixed')
    discount_value = request.form.get('discount_value', type=float)
    minimum_purchase = request.form.get('minimum_purchase', type=float) or 0.0
    maximum_usage = request.form.get('maximum_usage', type=int) or 100
    start_date = request.form.get('start_date', '').strip()
    expiry_date = request.form.get('expiry_date', '').strip()
    status = request.form.get('status', 'active')

    if not code or not name or discount_value is None or discount_value <= 0 or not start_date or not expiry_date:
        flash('Coupon Code, Name, Valid Discount Value, Start and Expiry Dates are required.', 'danger')
        return redirect(url_for('coupons.list_coupons_admin'))

    existing = query_db("SELECT id FROM coupons WHERE code = %s", (code,), one=True)
    if existing:
        flash(f'Coupon code "{code}" already exists.', 'danger')
        return redirect(url_for('coupons.list_coupons_admin'))

    try:
        execute_db(
            """
            INSERT INTO coupons 
            (code, name, description, discount_type, discount_value, minimum_purchase, maximum_usage, used_count, start_date, expiry_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s)
            """,
            (code, name, description, discount_type, discount_value, minimum_purchase, maximum_usage, start_date, expiry_date, status)
        )
        flash(f'Coupon "{code}" created successfully.', 'success')
    except Exception as e:
        flash(f'Failed to create coupon: {str(e)}', 'danger')

    return redirect(url_for('coupons.list_coupons_admin'))

@coupons_bp.route('/admin/coupons/<int:coupon_id>/edit', methods=['POST'])
@admin_required
def edit_coupon(coupon_id):
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    discount_type = request.form.get('discount_type', 'fixed')
    discount_value = request.form.get('discount_value', type=float)
    minimum_purchase = request.form.get('minimum_purchase', type=float) or 0.0
    maximum_usage = request.form.get('maximum_usage', type=int) or 100
    start_date = request.form.get('start_date', '').strip()
    expiry_date = request.form.get('expiry_date', '').strip()
    status = request.form.get('status', 'active')

    if not code or not name or discount_value is None or discount_value <= 0 or not start_date or not expiry_date:
        flash('All core fields are required.', 'danger')
        return redirect(url_for('coupons.list_coupons_admin'))

    existing = query_db("SELECT id FROM coupons WHERE code = %s AND id != %s", (code, coupon_id), one=True)
    if existing:
        flash(f'Coupon code "{code}" is already in use by another coupon.', 'danger')
        return redirect(url_for('coupons.list_coupons_admin'))

    try:
        execute_db(
            """
            UPDATE coupons 
            SET code = %s, name = %s, description = %s, discount_type = %s, discount_value = %s, 
                minimum_purchase = %s, maximum_usage = %s, start_date = %s, expiry_date = %s, status = %s
            WHERE id = %s
            """,
            (code, name, description, discount_type, discount_value, minimum_purchase, maximum_usage, start_date, expiry_date, status, coupon_id)
        )
        flash('Coupon updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating coupon: {str(e)}', 'danger')

    return redirect(url_for('coupons.list_coupons_admin'))

@coupons_bp.route('/admin/coupons/<int:coupon_id>/delete', methods=['POST'])
@admin_required
def delete_coupon(coupon_id):
    usages = query_db("SELECT id FROM coupon_usage WHERE coupon_id = %s", (coupon_id,))
    if usages:
        execute_db("UPDATE coupons SET status = 'inactive' WHERE id = %s", (coupon_id,))
        flash('Coupon has existing usage records; marked as Inactive.', 'warning')
    else:
        execute_db("DELETE FROM coupons WHERE id = %s", (coupon_id,))
        flash('Coupon deleted successfully.', 'success')

    return redirect(url_for('coupons.list_coupons_admin'))

@coupons_bp.route('/admin/coupons/usage')
@admin_required
def list_coupon_usage():
    usages = query_db("""
        SELECT cu.*, c.code as coupon_code, c.name as coupon_name, u.name as customer_name, u.email as customer_email, p.invoice_number, p.final_amount
        FROM coupon_usage cu
        JOIN coupons c ON cu.coupon_id = c.id
        JOIN users u ON cu.customer_id = u.id
        LEFT JOIN purchases p ON cu.purchase_id = p.id
        ORDER BY cu.used_at DESC
    """)
    return render_template('admin/coupon_usage.html', usages=usages)


# ================= CUSTOMER ROUTES =================

@coupons_bp.route('/customer/coupons')
@customer_required
def list_coupons_customer():
    today_str = date.today().strftime('%Y-%m-%d')
    coupons = query_db("""
        SELECT * FROM coupons 
        WHERE status = 'active' 
          AND start_date <= %s 
          AND expiry_date >= %s 
          AND used_count < maximum_usage
        ORDER BY expiry_date ASC
    """, (today_str, today_str))

    return render_template('customer/coupons.html', coupons=coupons)
