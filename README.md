# MarketPulse – Retail Customer Loyalty System

**MarketPulse** is a complete, full-featured, and modern retail customer loyalty management platform built for the **Retail Industry domain**. It empowers retail stores, supermarkets, and boutique outlets to engage customers, award points for in-store purchases, issue discount vouchers, validate smart coupons, and run seasonal promotional retail campaigns.

---

## 1. Project Overview & Capabilities

MarketPulse provides two distinct, role-based portals:

### 🏪 Admin Portal
* **Dashboard Analytics**: Real-time KPI cards (Total Customers, Points Issued, Rewards Inventory, Active Coupons, Live Campaigns, Total Sales Revenue) and 4 live activity feeds.
* **Customer Management**: Add, view, search, filter, edit, and delete customer profiles. View customer loyalty tier and detailed transaction ledger.
* **Purchase Recording & Loyalty Points**: Record customer purchases with automatic loyalty points calculation based on configurable backend rules (e.g., 10 points per ₹100 spent).
* **Rewards Management**: Create and manage reward catalogues with required points, monetary value, inventory stock control, and expiry dates. View customer redemption logs.
* **Smart Coupon Engine**: Create fixed and percentage discount coupons with minimum purchase thresholds, usage limits, and expiration dates. View real-time coupon usage logs.
* **Promotional Retail Campaigns**: Launch festive discounts, category offers, and 2x double points multiplier events.
* **Manual Points Adjustment**: Credit or debit customer loyalty points with mandatory reason logging for audit compliance.

### 🛍️ Customer Portal
* **Loyalty Summary & Tiers**: Live points balance, lifetime points earned, points redeemed, and dynamic loyalty tier recognition (**Bronze, Silver, Gold, Platinum**) with progress bar to the next tier.
* **Rewards Catalog & Instant Redemption**: Browse rewards, check unlock eligibility, and redeem points for vouchers with unique serial codes (`MP-REW-XXXXX`).
* **My Vouchers**: Store and view claimed vouchers to present at the store cashier counter.
* **Coupon Discovery**: Browse active store coupons with one-click code copying.
* **Purchase & Invoice Ledger**: View complete in-store purchase history, discounts saved, and points earned.
* **Points Transaction Audit Trail**: Full ledger of every point earned, redeemed, or adjusted.
* **Active Campaigns & Offers**: Discover ongoing festival sales and bonus events.
* **Profile Management**: Update phone numbers and change passwords securely.

---

## 2. Technology Stack — Strict Adherence

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript (Vanilla ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3 |
| **Backend** | Python 3.10+ / 3.13, Flask 3.x, Werkzeug Security |
| **Database** | MySQL (XAMPP MariaDB / MySQL Server 5.7+ / 8.x) |
| **Driver** | PyMySQL / mysqlclient |
| **Architecture** | Modular Blueprint-based MVC Pattern |

---

## 3. Demo Login Credentials

| Role | Email Address | Password | Points Balance / Notes |
| :--- | :--- | :--- | :--- |
| **Store Administrator** | `admin@marketpulse.com` | `Admin@123` | Full administrative control |
| **Customer (Gold Tier)** | `rahul.sharma@example.com` | `Customer@123` | 520 pts (Has purchases & vouchers) |
| **Customer (Silver Tier)** | `priya.patel@example.com` | `Customer@123` | 280 pts |
| **Customer (Bronze Tier)** | `amit.verma@example.com` | `Customer@123` | 90 pts |
| **Customer (New Member)** | `sneha.gupta@example.com` | `Customer@123` | 0 pts |

---

## 4. Project File Structure

```
MarketPulse/
│
├── app.py                      # Application Factory, filters & error handlers
├── config.py                   # Environment config & configurable points ratio
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database schema initializer
├── seed_db.py                  # Realistic demo data populator
├── test_app.py                 # Automated unit and integration test suite
│
├── database/
│   ├── schema.sql              # MySQL DDL table schemas with Foreign Keys & Indexes
│   ├── seed.sql                # SQL Demo dataset
│   └── db.py                   # Database connection wrapper & transaction manager
│
├── routes/
│   ├── auth.py                 # Login, Registration, Logout, Role decorators
│   ├── admin.py                # Admin Dashboard, Customer directory, Profile view
│   ├── customer.py             # Customer Dashboard, Points ledger, Profile
│   ├── purchases.py            # In-store purchase entry, POS coupon validator
│   ├── rewards.py              # Reward CRUD, Customer redemption, Voucher generation
│   ├── coupons.py              # Coupon CRUD & coupon usage tracking
│   └── campaigns.py            # Retail promotional campaigns CRUD & customer view
│
├── templates/
│   ├── base.html               # Main layout with responsive navbar & toast alerts
│   ├── index.html              # Marketing landing page with hero & demo access
│   │
│   ├── auth/
│   │   ├── login.html          # Clean sign-in with quick-fill demo buttons
│   │   └── register.html       # Customer registration with validation
│   │
│   ├── admin/
│   │   ├── dashboard.html      # KPI Cards, Analytics & 4 Recent activity feeds
│   │   ├── customers.html      # Customer directory with live JS search & Add modal
│   │   ├── customer_detail.html# Customer tabbed ledger & manual points adjustment
│   │   ├── purchases.html      # Purchase history & Record Purchase modal
│   │   ├── rewards.html        # Reward catalogue manager & inventory stock
│   │   ├── redemptions.html    # All store reward redemptions log
│   │   ├── coupons.html        # Coupon manager with usage limits & date checks
│   │   ├── coupon_usage.html   # Detailed coupon usage audit log
│   │   └── campaigns.html      # Retail promotional campaigns manager
│   │
│   ├── customer/
│   │   ├── dashboard.html      # Points summary, Tier badge, quick actions & feeds
│   │   ├── points.html         # Detailed points ledger with +/- indicators
│   │   ├── purchases.html      # Customer invoice history & discounts
│   │   ├── rewards.html        # Rewards catalogue with unlock progress meters
│   │   ├── my_redemptions.html # Claimed vouchers with copyable codes
│   │   ├── coupons.html        # Active coupons & one-click copy codes
│   │   ├── campaigns.html      # Active promotional campaigns & festival offers
│   │   └── profile.html        # Profile details, phone update & password change
│   │
│   └── errors/
│       ├── 404.html            # User-friendly Not Found page
│       └── 500.html            # User-friendly Server Error page
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern retail styling, badges, cards, tier styles
│   └── js/
│       └── script.js           # Live search/filters, dynamic coupon validator, copy
│
└── README.md                   # Complete documentation & setup instructions
```

---

## 5. Step-by-Step Setup & Installation Guide

### Prerequisites
* Windows 10/11 (or macOS / Linux)
* Python 3.10 or newer
* XAMPP (Apache + MySQL) or standalone MySQL Server
* VS Code or PyCharm

---

### Step 1: Start MySQL in XAMPP
1. Launch the **XAMPP Control Panel**.
2. Click **Start** next to **MySQL** (Default port `3306`).
3. *(Optional)* Click **Start** next to **Apache** if you wish to use phpMyAdmin at `http://localhost/phpmyadmin`.

---

### Step 2: Configure Environment & Python Virtual Environment
Open a terminal (PowerShell or Command Prompt) in the project root directory:

```powershell
# 1. Create a Python virtual environment (Optional but Recommended)
python -m venv venv

# 2. Activate the virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows Command Prompt:
.\venv\Scripts\activate.bat

# 3. Install required Python packages
pip install -r requirements.txt
```

---

### Step 3: Initialize Database & Seed Demo Data
You can initialize the database using either Python or phpMyAdmin:

#### Option A: Automatic Python Script (Recommended)
Run the automated seed script which connects to MySQL (or prepares the local storage if MySQL is offline) and inserts the demo data:

```powershell
python seed_db.py
```

#### Option B: Manual phpMyAdmin Import
1. Open `http://localhost/phpmyadmin` in your browser.
2. Click on **SQL** tab and execute:
   ```sql
   CREATE DATABASE IF NOT EXISTS marketpulse;
   ```
3. Import `database/schema.sql`.
4. Import `database/seed.sql`.

---

### Step 4: Run the Flask Web Application

```powershell
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 6. Main Business Rules & Logic

1. **Configurable Points Calculation**:
   - Configured in `config.py`: `POINTS_PER_100_SPENT = 10.0` (10 points per ₹100 spent).
   - Rate: `0.10 points / ₹1.00`.
   - Points are calculated on the **net final amount** after coupon discounts.
2. **Atomic Purchase & Points Issuance**:
   - Recording a purchase writes to `purchases`, calculates points, updates `users.points_balance`, and logs a record to `loyalty_transactions` atomically.
3. **Reward Redemption Rules**:
   - A customer cannot redeem if `Customer Points < Required Points`.
   - A customer cannot redeem if `stock <= 0` or if the reward has expired.
   - On redemption: points are deducted from customer balance, inventory stock is decremented by 1, an entry is created in `reward_redemptions`, and a transaction is logged to `loyalty_transactions`.
4. **Smart Coupon Validation**:
   - Checks active status, date range (`start_date <= today <= expiry_date`), minimum cart purchase threshold, and total maximum usage cap (`used_count < maximum_usage`).
5. **Role-Based Security**:
   - Passwords hashed with `Werkzeug (scrypt/pbkdf2)`.
   - Admin routes protected with `@admin_required`.
   - Customer routes protected with `@customer_required`.
   - Parameterized SQL queries preventing SQL Injection attacks.

---

## 7. Running Automated Tests

To execute the automated test suite verifying all 8 core business flows:

```powershell
python test_app.py
```

Output:
```
Ran 8 tests in ...
OK
```

---

## 8. Troubleshooting Common Errors

* **"Access denied for user 'root'@'localhost'"**:
  Ensure your MySQL root password matches `config.py` (Default XAMPP password is empty string `""`). If you have a custom password, create a `.env` file with `DB_PASSWORD=your_password`.
* **"Port 5000 already in use"**:
  Run `python app.py` on another port or terminate the background process using `taskkill /F /PID <pid>`.
* **"ModuleNotFoundError: No module named 'flask'"**:
  Ensure your virtual environment is activated and run `pip install -r requirements.txt`.

---

## 9. College Major Project Highlights
* **Clean MVC Architecture** with modular blueprints.
* **Zero Cloud Lock-in**: Fully runnable offline on a local laptop with XAMPP.
* **Interactive UI**: Live search filters, instant coupon calculation preview, and copyable voucher codes without page reloads.
* **Audit Trail**: Every single point earned or spent is traceable via `loyalty_transactions`.
