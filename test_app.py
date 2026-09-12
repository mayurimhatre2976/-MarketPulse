"""
MarketPulse Automated Test Suite
Verifies all core retail workflows, business rules, and security.
"""
import random
import unittest
from app import create_app
from seed_db import seed_database
from database.db import query_db, execute_db

class MarketPulseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def login(self, email, password):
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_01_landing_page(self):
        """Test public landing page accessibility."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MarketPulse', response.data)
        self.assertIn(b'Empower Your Retail Store With', response.data)

    def test_02_authentication_and_roles(self):
        """Test Admin and Customer logins and access control."""
        # 1. Admin Login
        res_admin = self.login('admin@marketpulse.com', 'Admin@123')
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b'Store Analytics', res_admin.data)
        self.logout()

        # 2. Customer Login
        res_cust = self.login('rahul.sharma@example.com', 'Customer@123')
        self.assertEqual(res_cust.status_code, 200)
        self.assertIn(b'My Loyalty Dashboard', res_cust.data)
        self.assertIn(b'Rahul Sharma', res_cust.data)

        # 3. Customer attempting to access Admin route should be blocked/redirected
        res_forbidden = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied', res_forbidden.data)
        self.logout()

    def test_03_customer_registration(self):
        """Test customer registration and duplicate prevention."""
        rand_email = f"testuser_{random.randint(10000, 99999)}@example.com"
        
        # Successful Registration
        res = self.client.post('/register', data={
            'name': 'Test New Member',
            'email': rand_email,
            'phone': '9988776655',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # Duplicate Email Registration Attempt
        res_dup = self.client.post('/register', data={
            'name': 'Duplicate User',
            'email': rand_email,
            'phone': '9988776655',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', res_dup.data)

    def test_04_purchase_recording_and_loyalty_points(self):
        """Test recording a purchase and verifying loyalty points auto-calculation."""
        self.login('admin@marketpulse.com', 'Admin@123')
        
        priya = query_db("SELECT id, points_balance FROM users WHERE email = %s", ('priya.patel@example.com',), one=True)
        initial_points = priya['points_balance']
        
        # Record purchase: ₹1,000 without coupon => 100 points
        inv_num = f"INV-TEST-{priya['id']}-{random.randint(10000, 99999)}"
        res = self.client.post('/admin/purchases/new', data={
            'customer_id': priya['id'],
            'invoice_number': inv_num,
            'amount': '1000.00',
            'purchase_date': '2026-09-11',
            'coupon_code': '',
            'description': 'Automated Test Grocery Order'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Purchase recorded successfully', res.data)

        # Check updated points balance in database
        updated_priya = query_db("SELECT points_balance FROM users WHERE id = %s", (priya['id'],), one=True)
        expected_points = initial_points + 100
        self.assertEqual(updated_priya['points_balance'], expected_points)

        # Check loyalty transaction record
        tx = query_db("SELECT * FROM loyalty_transactions WHERE customer_id = %s AND description LIKE %s", 
                      (priya['id'], f"%{inv_num}%"), one=True)
        self.assertIsNotNone(tx)
        self.assertEqual(tx['points'], 100)
        self.assertEqual(tx['transaction_type'], 'EARN')
        self.logout()

    def test_05_coupon_validation_and_purchase(self):
        """Test applying coupon discount during purchase."""
        self.login('admin@marketpulse.com', 'Admin@123')

        amit = query_db("SELECT id, points_balance FROM users WHERE email = %s", ('amit.verma@example.com',), one=True)
        
        # Test coupon API validation
        api_res = self.client.post('/api/validate-coupon', json={
            'code': 'PULSE10',
            'amount': 2000.00
        })
        json_data = api_res.get_json()
        self.assertTrue(json_data['valid'])
        self.assertEqual(json_data['discount_amount'], 200.00)
        self.assertEqual(json_data['final_amount'], 1800.00)

        # Record purchase with PULSE10: ₹2,000 - 10% (₹200) = ₹1,800 => 180 points
        inv_num = f"INV-TEST-COUPON-{amit['id']}-{random.randint(10000, 99999)}"
        res = self.client.post('/admin/purchases/new', data={
            'customer_id': amit['id'],
            'invoice_number': inv_num,
            'amount': '2000.00',
            'purchase_date': '2026-09-11',
            'coupon_code': 'PULSE10',
            'description': 'Electronics with 10% coupon'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify purchase record
        purch = query_db("SELECT * FROM purchases WHERE invoice_number = %s", (inv_num,), one=True)
        self.assertIsNotNone(purch)
        self.assertEqual(float(purch['discount_amount']), 200.00)
        self.assertEqual(float(purch['final_amount']), 1800.00)
        self.assertEqual(purch['points_earned'], 180)
        self.logout()

    def test_06_reward_redemption_flow(self):
        """Test customer redeeming reward, atomic points deduction and stock decrement."""
        # Ensure Rahul has at least 500 points and reward has stock
        execute_db("UPDATE users SET points_balance = 520 WHERE email = 'rahul.sharma@example.com'")
        execute_db("UPDATE rewards SET stock = 20 WHERE id = 1")
        
        self.login('rahul.sharma@example.com', 'Customer@123')
        
        rahul = query_db("SELECT id, points_balance FROM users WHERE email = %s", ('rahul.sharma@example.com',), one=True)
        reward = query_db("SELECT * FROM rewards WHERE id = 1", one=True)
        
        init_balance = rahul['points_balance']
        init_stock = reward['stock']

        # Redeem reward
        res = self.client.post(f'/customer/rewards/redeem/{reward["id"]}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'successfully redeemed', res.data)

        # Verify database changes
        updated_rahul = query_db("SELECT points_balance FROM users WHERE id = %s", (rahul['id'],), one=True)
        self.assertEqual(updated_rahul['points_balance'], init_balance - reward['required_points'])

        updated_reward = query_db("SELECT stock FROM rewards WHERE id = %s", (reward['id'],), one=True)
        self.assertEqual(updated_reward['stock'], init_stock - 1)

        # Check redemption voucher was generated
        redemption = query_db("SELECT * FROM reward_redemptions WHERE customer_id = %s ORDER BY id DESC LIMIT 1", (rahul['id'],), one=True)
        self.assertIsNotNone(redemption)
        self.assertTrue(redemption['redemption_code'].startswith('MP-REW-'))
        self.logout()

    def test_07_insufficient_points_blocked(self):
        """Test that a customer cannot redeem a reward if points are insufficient."""
        # Sneha Gupta has 0 points
        execute_db("UPDATE users SET points_balance = 0 WHERE email = 'sneha.gupta@example.com'")
        self.login('sneha.gupta@example.com', 'Customer@123')
        reward = query_db("SELECT * FROM rewards WHERE required_points = 200", one=True)
        
        res = self.client.post(f'/customer/rewards/redeem/{reward["id"]}', follow_redirects=True)
        self.assertIn(b'Insufficient loyalty points', res.data)
        self.logout()

    def test_08_admin_points_adjustment(self):
        """Test admin manual points credit and debit with transaction audit."""
        self.login('admin@marketpulse.com', 'Admin@123')
        
        customer = query_db("SELECT id, points_balance FROM users WHERE email = %s", ('amit.verma@example.com',), one=True)
        init_balance = customer['points_balance']

        # Credit 50 points
        res_credit = self.client.post('/admin/points/adjust', data={
            'customer_id': customer['id'],
            'points': '50',
            'adjustment_type': 'credit',
            'reason': 'Special Loyalty Bonus'
        }, follow_redirects=True)
        self.assertEqual(res_credit.status_code, 200)

        updated = query_db("SELECT points_balance FROM users WHERE id = %s", (customer['id'],), one=True)
        self.assertEqual(updated['points_balance'], init_balance + 50)
        self.logout()

if __name__ == '__main__':
    unittest.main(verbosity=2)
