"""
MarketPulse Demo Data Seed Script
Populates the database with realistic sample retail data.
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database.db import get_db, init_database_tables, query_db

def seed_database():
    init_database_tables()
    
    # Check if already seeded
    admin = query_db("SELECT id FROM users WHERE email = %s", ('admin@marketpulse.com',), one=True)
    if admin:
        print("[INFO] Database already contains seed data. Refreshing demo records...")

    admin_hash = generate_password_hash('Admin@123')
    customer_hash = generate_password_hash('Customer@123')
    today = datetime.now()

    with get_db() as db:
        # 1. Users (Admin + 4 Customers)
        users_data = [
            ('Store Administrator', 'admin@marketpulse.com', '9876543200', admin_hash, 'admin', 0),
            ('Rahul Sharma', 'rahul.sharma@example.com', '9876543210', customer_hash, 'customer', 520),
            ('Priya Patel', 'priya.patel@example.com', '9876543211', customer_hash, 'customer', 280),
            ('Amit Verma', 'amit.verma@example.com', '9876543212', customer_hash, 'customer', 90),
            ('Sneha Gupta', 'sneha.gupta@example.com', '9876543213', customer_hash, 'customer', 0)
        ]
        for name, email, phone, pwd, role, points in users_data:
            existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
            if not existing:
                db.execute(
                    "INSERT INTO users (name, email, phone, password_hash, role, points_balance) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, email, phone, pwd, role, points)
                )

        # 2. Rewards
        rewards_data = [
            ('₹200 Retail Shopping Voucher', 'Get flat ₹200 off across all grocery, apparel and general store merchandise.', 200, 200.00, 48, (today + timedelta(days=60)).strftime('%Y-%m-%d'), 'active'),
            ('Flat ₹500 Discount Pass', 'Premium discount voucher redeemable on store purchases above ₹2000.', 500, 500.00, 20, (today + timedelta(days=90)).strftime('%Y-%m-%d'), 'active'),
            ('MarketPulse Eco-Canvas Tote Bag', 'Durable, stylish and sustainable cotton shopping bag with MarketPulse crest.', 100, 150.00, 50, (today + timedelta(days=120)).strftime('%Y-%m-%d'), 'active'),
            ('Free Premium Express Delivery Pass', 'Free priority home delivery for 3 months on all grocery orders.', 150, 300.00, 100, (today + timedelta(days=180)).strftime('%Y-%m-%d'), 'active'),
            ('Gourmet Artisan Coffee Mug Set', 'Set of 2 ceramic handcrafted mugs with MarketPulse coffee bar token.', 250, 350.00, 15, (today + timedelta(days=45)).strftime('%Y-%m-%d'), 'active')
        ]
        for name, desc, pts, val, stock, exp, status in rewards_data:
            existing = query_db("SELECT id FROM rewards WHERE name = %s", (name,), one=True)
            if not existing:
                db.execute(
                    "INSERT INTO rewards (name, description, required_points, reward_value, stock, expiry_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, desc, pts, val, stock, exp, status)
                )

        # 3. Coupons
        coupons_data = [
            ('PULSE10', 'MarketPulse 10% Off', 'Enjoy 10% discount on total cart value.', 'percentage', 10.00, 500.00, 500, 2, (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'active'),
            ('FLAT100', 'Flat ₹100 Super Saver', 'Get instant ₹100 off on minimum purchase of ₹1,000.', 'fixed', 100.00, 1000.00, 200, 1, (today - timedelta(days=15)).strftime('%Y-%m-%d'), (today + timedelta(days=45)).strftime('%Y-%m-%d'), 'active'),
            ('WELCOME50', 'New Member Welcome', 'Welcome bonus discount for loyal members on orders above ₹300.', 'fixed', 50.00, 300.00, 1000, 0, (today - timedelta(days=30)).strftime('%Y-%m-%d'), (today + timedelta(days=60)).strftime('%Y-%m-%d'), 'active'),
            ('FESTIVE20', 'Festive Special 20%', 'Celebration discount: 20% off on retail purchases above ₹1,500.', 'percentage', 20.00, 1500.00, 100, 0, (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=25)).strftime('%Y-%m-%d'), 'active')
        ]
        for code, name, desc, dtype, dval, minp, maxu, used, sdate, edate, status in coupons_data:
            existing = query_db("SELECT id FROM coupons WHERE code = %s", (code,), one=True)
            if not existing:
                db.execute(
                    "INSERT INTO coupons (code, name, description, discount_type, discount_value, minimum_purchase, maximum_usage, used_count, start_date, expiry_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (code, name, desc, dtype, dval, minp, maxu, used, sdate, edate, status)
                )

        # 4. Campaigns
        campaigns_data = [
            ('Festival Mega Savings Bonanza', 'Special seasonal celebration discounts on clothing, home essentials, and grocery hampers.', 'Discount Offer', (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=20)).strftime('%Y-%m-%d'), 'All Customers', 'Up to 20% off with coupon FESTIVE20', 'active'),
            ('Weekend Double Points Blast', 'Earn 2x points on all weekend store visits! Accelerate your journey towards gift vouchers.', 'Points Multiplier', (today - timedelta(days=2)).strftime('%Y-%m-%d'), (today + timedelta(days=14)).strftime('%Y-%m-%d'), 'Loyalty Members', '20 Points per ₹100 spent', 'active'),
            ('New Customer Welcome Month', 'Special rewards and bonus introductory vouchers for newly registered retail customers.', 'Bonus Points', (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today + timedelta(days=50)).strftime('%Y-%m-%d'), 'New Customers', 'Extra 50 Bonus Points on 1st Order', 'active'),
            ('Organic Green Fresh Harvest Days', 'Healthy savings on all certified organic vegetables, cold-pressed oils, and farm fresh goods.', 'Category Discount', (today - timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=10)).strftime('%Y-%m-%d'), 'All Customers', 'Flat ₹100 off on fresh produce above ₹800', 'active')
        ]
        for name, desc, ctype, sdate, edate, aud, offer, status in campaigns_data:
            existing = query_db("SELECT id FROM campaigns WHERE name = %s", (name,), one=True)
            if not existing:
                db.execute(
                    "INSERT INTO campaigns (name, description, campaign_type, start_date, end_date, target_audience, offer, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, desc, ctype, sdate, edate, aud, offer, status)
                )

        # 5. Purchases for Rahul (id=2), Priya (id=3), Amit (id=4)
        rahul = query_db("SELECT id FROM users WHERE email = %s", ('rahul.sharma@example.com',), one=True)
        priya = query_db("SELECT id FROM users WHERE email = %s", ('priya.patel@example.com',), one=True)
        amit = query_db("SELECT id FROM users WHERE email = %s", ('amit.verma@example.com',), one=True)

        if rahul and priya and amit:
            purchases_data = [
                (rahul['id'], 'INV-2026-001', 3500.00, 0.00, 3500.00, None, 'Grocery essentials, organic pulses, pantry items', (today - timedelta(days=20)).strftime('%Y-%m-%d'), 350),
                (rahul['id'], 'INV-2026-002', 2000.00, 100.00, 1900.00, 2, 'Apparel items & summer wear with coupon FLAT100', (today - timedelta(days=12)).strftime('%Y-%m-%d'), 190),
                (rahul['id'], 'INV-2026-003', 1800.00, 180.00, 1620.00, 1, 'Home decor and kitchenware with coupon PULSE10', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 160),
                (priya['id'], 'INV-2026-004', 2800.00, 0.00, 2800.00, None, 'Fashion accessories, perfumes, cosmetics', (today - timedelta(days=10)).strftime('%Y-%m-%d'), 280),
                (amit['id'], 'INV-2026-005', 900.00, 0.00, 900.00, None, 'Stationery supplies & books', (today - timedelta(days=4)).strftime('%Y-%m-%d'), 90)
            ]
            for cid, inv, amt, disc, fin_amt, cid_coupon, desc, pdate, pts in purchases_data:
                existing = query_db("SELECT id FROM purchases WHERE invoice_number = %s", (inv,), one=True)
                if not existing:
                    db.execute(
                        "INSERT INTO purchases (customer_id, invoice_number, amount, discount_amount, final_amount, coupon_id, description, purchase_date, points_earned) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (cid, inv, amt, disc, fin_amt, cid_coupon, desc, pdate, pts)
                    )

            # 6. Loyalty Transactions
            tx_data = [
                (rahul['id'], 1, 'EARN', 350, 'Points earned on Invoice #INV-2026-001'),
                (rahul['id'], 2, 'EARN', 190, 'Points earned on Invoice #INV-2026-002'),
                (rahul['id'], None, 'REDEEM', -200, 'Redeemed ₹200 Retail Shopping Voucher (Code: MP-REW-88291)'),
                (rahul['id'], 3, 'EARN', 160, 'Points earned on Invoice #INV-2026-003'),
                (rahul['id'], None, 'BONUS', 20, 'Weekend celebration promotional bonus points'),
                (priya['id'], 4, 'EARN', 280, 'Points earned on Invoice #INV-2026-004'),
                (amit['id'], 5, 'EARN', 90, 'Points earned on Invoice #INV-2026-005')
            ]
            for cid, pid, ttype, pts, desc in tx_data:
                existing = query_db("SELECT id FROM loyalty_transactions WHERE customer_id = %s AND description = %s", (cid, desc), one=True)
                if not existing:
                    db.execute(
                        "INSERT INTO loyalty_transactions (customer_id, purchase_id, transaction_type, points, description) VALUES (%s, %s, %s, %s, %s)",
                        (cid, pid, ttype, pts, desc)
                    )

            # 7. Reward Redemption for Rahul
            existing_redemption = query_db("SELECT id FROM reward_redemptions WHERE redemption_code = %s", ('MP-REW-88291',), one=True)
            if not existing_redemption:
                db.execute(
                    "INSERT INTO reward_redemptions (customer_id, reward_id, points_used, redemption_code, status) VALUES (%s, %s, %s, %s, %s)",
                    (rahul['id'], 1, 200, 'MP-REW-88291', 'completed')
                )

            # 8. Coupon Usages
            usages = [
                (2, rahul['id'], 2, 100.00),
                (1, rahul['id'], 3, 180.00)
            ]
            for cpn_id, cust_id, purch_id, disc in usages:
                existing_u = query_db("SELECT id FROM coupon_usage WHERE coupon_id = %s AND purchase_id = %s", (cpn_id, purch_id), one=True)
                if not existing_u:
                    db.execute(
                        "INSERT INTO coupon_usage (coupon_id, customer_id, purchase_id, discount_applied) VALUES (%s, %s, %s, %s)",
                        (cpn_id, cust_id, purch_id, disc)
                    )

    print("[SUCCESS] MarketPulse demo database successfully seeded!")

if __name__ == '__main__':
    seed_database()
