from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import query_db, execute_db
from routes.auth import admin_required, customer_required

campaigns_bp = Blueprint('campaigns', __name__)

# ================= ADMIN ROUTES =================

@campaigns_bp.route('/admin/campaigns')
@admin_required
def list_campaigns_admin():
    campaigns = query_db("SELECT * FROM campaigns ORDER BY created_at DESC")
    return render_template('admin/campaigns.html', campaigns=campaigns, today_date=date.today().strftime('%Y-%m-%d'))

@campaigns_bp.route('/admin/campaigns/add', methods=['POST'])
@admin_required
def add_campaign():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    campaign_type = request.form.get('campaign_type', 'Discount Offer').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    target_audience = request.form.get('target_audience', 'All Customers').strip()
    offer = request.form.get('offer', '').strip()
    status = request.form.get('status', 'active')

    if not name or not campaign_type or not start_date or not end_date or not offer:
        flash('Campaign Name, Type, Start & End Dates, and Offer details are required.', 'danger')
        return redirect(url_for('campaigns.list_campaigns_admin'))

    try:
        execute_db(
            """
            INSERT INTO campaigns (name, description, campaign_type, start_date, end_date, target_audience, offer, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, description, campaign_type, start_date, end_date, target_audience, offer, status)
        )
        flash(f'Campaign "{name}" created successfully.', 'success')
    except Exception as e:
        flash(f'Failed to create campaign: {str(e)}', 'danger')

    return redirect(url_for('campaigns.list_campaigns_admin'))

@campaigns_bp.route('/admin/campaigns/<int:campaign_id>/edit', methods=['POST'])
@admin_required
def edit_campaign(campaign_id):
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    campaign_type = request.form.get('campaign_type', '').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    target_audience = request.form.get('target_audience', '').strip()
    offer = request.form.get('offer', '').strip()
    status = request.form.get('status', 'active')

    if not name or not campaign_type or not start_date or not end_date or not offer:
        flash('All required campaign fields must be provided.', 'danger')
        return redirect(url_for('campaigns.list_campaigns_admin'))

    try:
        execute_db(
            """
            UPDATE campaigns 
            SET name = %s, description = %s, campaign_type = %s, start_date = %s, end_date = %s, target_audience = %s, offer = %s, status = %s
            WHERE id = %s
            """,
            (name, description, campaign_type, start_date, end_date, target_audience, offer, status, campaign_id)
        )
        flash('Campaign updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating campaign: {str(e)}', 'danger')

    return redirect(url_for('campaigns.list_campaigns_admin'))

@campaigns_bp.route('/admin/campaigns/<int:campaign_id>/delete', methods=['POST'])
@admin_required
def delete_campaign(campaign_id):
    try:
        execute_db("DELETE FROM campaigns WHERE id = %s", (campaign_id,))
        flash('Campaign deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting campaign: {str(e)}', 'danger')

    return redirect(url_for('campaigns.list_campaigns_admin'))


# ================= CUSTOMER ROUTES =================

@campaigns_bp.route('/customer/campaigns')
@customer_required
def list_campaigns_customer():
    today_str = date.today().strftime('%Y-%m-%d')
    campaigns = query_db("""
        SELECT * FROM campaigns 
        WHERE status = 'active' 
          AND start_date <= %s 
          AND end_date >= %s 
        ORDER BY end_date ASC
    """, (today_str, today_str))

    return render_template('customer/campaigns.html', campaigns=campaigns)
