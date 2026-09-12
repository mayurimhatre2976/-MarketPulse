-- MarketPulse Seed Demo Data
USE `marketpulse`;

-- Insert Admin & Customers
-- Admin Password: Admin@123
-- Customer Passwords: Customer@123
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `points_balance`, `created_at`) VALUES
(1, 'Store Administrator', 'admin@marketpulse.com', '9876543200', 'scrypt:32768:8:1$rIsLa3soebl1ALAs$d26dd8fdd58b9e8093f323f87e2a5c58c1f08c9df2a6856454095febd8ff6020f27b108713073eec2c3e0baa73ae87fc3fa8d5a984b3acb7db449e7ef203dba4', 'admin', 0, NOW() - INTERVAL 30 DAY),
(2, 'Rahul Sharma', 'rahul.sharma@example.com', '9876543210', 'scrypt:32768:8:1$QnkLjfhCen8Ev8gb$7ee51b4d2921332e6ed398f19af5b330c45b280c2548945f409a4698609eef542a2f45a1526520d4f13b3d48220fc75b4d98a6a252b5c03d17dac576054442ab', 'customer', 520, NOW() - INTERVAL 25 DAY),
(3, 'Priya Patel', 'priya.patel@example.com', '9876543211', 'scrypt:32768:8:1$QnkLjfhCen8Ev8gb$7ee51b4d2921332e6ed398f19af5b330c45b280c2548945f409a4698609eef542a2f45a1526520d4f13b3d48220fc75b4d98a6a252b5c03d17dac576054442ab', 'customer', 280, NOW() - INTERVAL 15 DAY),
(4, 'Amit Verma', 'amit.verma@example.com', '9876543212', 'scrypt:32768:8:1$QnkLjfhCen8Ev8gb$7ee51b4d2921332e6ed398f19af5b330c45b280c2548945f409a4698609eef542a2f45a1526520d4f13b3d48220fc75b4d98a6a252b5c03d17dac576054442ab', 'customer', 90, NOW() - INTERVAL 7 DAY),
(5, 'Sneha Gupta', 'sneha.gupta@example.com', '9876543213', 'scrypt:32768:8:1$QnkLjfhCen8Ev8gb$7ee51b4d2921332e6ed398f19af5b330c45b280c2548945f409a4698609eef542a2f45a1526520d4f13b3d48220fc75b4d98a6a252b5c03d17dac576054442ab', 'customer', 0, NOW() - INTERVAL 2 DAY)
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- Insert Sample Rewards
INSERT INTO `rewards` (`id`, `name`, `description`, `required_points`, `reward_value`, `stock`, `expiry_date`, `status`, `created_at`) VALUES
(1, '₹200 Retail Shopping Voucher', 'Get flat ₹200 off across all grocery, apparel and general store merchandise.', 200, 200.00, 48, DATE_ADD(CURDATE(), INTERVAL 60 DAY), 'active', NOW() - INTERVAL 20 DAY),
(2, 'Flat ₹500 Discount Pass', 'Premium discount voucher redeemable on store purchases above ₹2000.', 500, 500.00, 20, DATE_ADD(CURDATE(), INTERVAL 90 DAY), 'active', NOW() - INTERVAL 20 DAY),
(3, 'MarketPulse Eco-Canvas Tote Bag', 'Durable, stylish and sustainable cotton shopping bag with MarketPulse crest.', 100, 150.00, 50, DATE_ADD(CURDATE(), INTERVAL 120 DAY), 'active', NOW() - INTERVAL 15 DAY),
(4, 'Free Premium Express Delivery Pass', 'Free priority home delivery for 3 months on all grocery orders.', 150, 300.00, 100, DATE_ADD(CURDATE(), INTERVAL 180 DAY), 'active', NOW() - INTERVAL 10 DAY),
(5, 'Gourmet Artisan Coffee Mug Set', 'Set of 2 ceramic handcrafted mugs with MarketPulse coffee bar token.', 250, 350.00, 15, DATE_ADD(CURDATE(), INTERVAL 45 DAY), 'active', NOW() - INTERVAL 5 DAY)
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- Insert Sample Coupons
INSERT INTO `coupons` (`id`, `code`, `name`, `description`, `discount_type`, `discount_value`, `minimum_purchase`, `maximum_usage`, `used_count`, `start_date`, `expiry_date`, `status`, `created_at`) VALUES
(1, 'PULSE10', 'MarketPulse 10% Off', 'Enjoy 10% discount on total cart value.', 'percentage', 10.00, 500.00, 500, 2, CURDATE() - INTERVAL 10 DAY, DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active', NOW() - INTERVAL 10 DAY),
(2, 'FLAT100', 'Flat ₹100 Super Saver', 'Get instant ₹100 off on minimum purchase of ₹1,000.', 'fixed', 100.00, 1000.00, 200, 1, CURDATE() - INTERVAL 15 DAY, DATE_ADD(CURDATE(), INTERVAL 45 DAY), 'active', NOW() - INTERVAL 15 DAY),
(3, 'WELCOME50', 'New Member Welcome', 'Welcome bonus discount for loyal members on orders above ₹300.', 'fixed', 50.00, 300.00, 1000, 0, CURDATE() - INTERVAL 30 DAY, DATE_ADD(CURDATE(), INTERVAL 60 DAY), 'active', NOW() - INTERVAL 30 DAY),
(4, 'FESTIVE20', 'Festive Special 20%', 'Celebration discount: 20% off on retail purchases above ₹1,500.', 'percentage', 20.00, 1500.00, 100, 0, CURDATE() - INTERVAL 5 DAY, DATE_ADD(CURDATE(), INTERVAL 25 DAY), 'active', NOW() - INTERVAL 5 DAY)
ON DUPLICATE KEY UPDATE `code`=VALUES(`code`);

-- Insert Sample Campaigns
INSERT INTO `campaigns` (`id`, `name`, `description`, `campaign_type`, `start_date`, `end_date`, `target_audience`, `offer`, `status`, `created_at`) VALUES
(1, 'Festival Mega Savings Bonanza', 'Special seasonal celebration discounts on clothing, home essentials, and grocery hampers.', 'Discount Offer', CURDATE() - INTERVAL 5 DAY, DATE_ADD(CURDATE(), INTERVAL 20 DAY), 'All Customers', 'Up to 20% off with coupon FESTIVE20', 'active', NOW() - INTERVAL 5 DAY),
(2, 'Weekend Double Points Blast', 'Earn 2x points on all weekend store visits! Accelerate your journey towards gift vouchers.', 'Points Multiplier', CURDATE() - INTERVAL 2 DAY, DATE_ADD(CURDATE(), INTERVAL 14 DAY), 'Loyalty Members', '20 Points per ₹100 spent', 'active', NOW() - INTERVAL 2 DAY),
(3, 'New Customer Welcome Month', 'Special rewards and bonus introductory vouchers for newly registered retail customers.', 'Bonus Points', CURDATE() - INTERVAL 10 DAY, DATE_ADD(CURDATE(), INTERVAL 50 DAY), 'New Customers', 'Extra 50 Bonus Points on 1st Order', 'active', NOW() - INTERVAL 10 DAY),
(4, 'Organic Green Fresh Harvest Days', 'Healthy savings on all certified organic vegetables, cold-pressed oils, and farm fresh goods.', 'Category Discount', CURDATE() - INTERVAL 1 DAY, DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'All Customers', 'Flat ₹100 off on fresh produce above ₹800', 'active', NOW() - INTERVAL 1 DAY)
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- Insert Sample Purchases
INSERT INTO `purchases` (`id`, `customer_id`, `invoice_number`, `amount`, `discount_amount`, `final_amount`, `coupon_id`, `description`, `purchase_date`, `points_earned`, `created_at`) VALUES
(1, 2, 'INV-2026-001', 3500.00, 0.00, 3500.00, NULL, 'Grocery essentials, organic pulses, pantry items', CURDATE() - INTERVAL 20 DAY, 350, NOW() - INTERVAL 20 DAY),
(2, 2, 'INV-2026-002', 2000.00, 100.00, 1900.00, 2, 'Apparel items & summer wear with coupon FLAT100', CURDATE() - INTERVAL 12 DAY, 190, NOW() - INTERVAL 12 DAY),
(3, 2, 'INV-2026-003', 1800.00, 180.00, 1620.00, 1, 'Home decor and kitchenware with coupon PULSE10', CURDATE() - INTERVAL 5 DAY, 160, NOW() - INTERVAL 5 DAY),
(4, 3, 'INV-2026-004', 2800.00, 0.00, 2800.00, NULL, 'Fashion accessories, perfumes, cosmetics', CURDATE() - INTERVAL 10 DAY, 280, NOW() - INTERVAL 10 DAY),
(5, 4, 'INV-2026-005', 900.00, 0.00, 900.00, NULL, 'Stationery supplies & books', CURDATE() - INTERVAL 4 DAY, 90, NOW() - INTERVAL 4 DAY)
ON DUPLICATE KEY UPDATE `invoice_number`=VALUES(`invoice_number`);

-- Insert Sample Loyalty Transactions
INSERT INTO `loyalty_transactions` (`id`, `customer_id`, `purchase_id`, `transaction_type`, `points`, `description`, `created_at`) VALUES
(1, 2, 1, 'EARN', 350, 'Points earned on Invoice #INV-2026-001', NOW() - INTERVAL 20 DAY),
(2, 2, 2, 'EARN', 190, 'Points earned on Invoice #INV-2026-002', NOW() - INTERVAL 12 DAY),
(3, 2, NULL, 'REDEEM', -200, 'Redeemed ₹200 Retail Shopping Voucher (Code: MP-REW-88291)', NOW() - INTERVAL 8 DAY),
(4, 2, 3, 'EARN', 160, 'Points earned on Invoice #INV-2026-003', NOW() - INTERVAL 5 DAY),
(5, 2, NULL, 'BONUS', 20, 'Weekend celebration promotional bonus points', NOW() - INTERVAL 3 DAY),
(6, 3, 4, 'EARN', 280, 'Points earned on Invoice #INV-2026-004', NOW() - INTERVAL 10 DAY),
(7, 4, 5, 'EARN', 90, 'Points earned on Invoice #INV-2026-005', NOW() - INTERVAL 4 DAY)
ON DUPLICATE KEY UPDATE `id`=VALUES(`id`);

-- Insert Sample Reward Redemptions
INSERT INTO `reward_redemptions` (`id`, `customer_id`, `reward_id`, `points_used`, `redemption_code`, `redemption_date`, `status`) VALUES
(1, 2, 1, 200, 'MP-REW-88291', NOW() - INTERVAL 8 DAY, 'completed')
ON DUPLICATE KEY UPDATE `redemption_code`=VALUES(`redemption_code`);

-- Insert Sample Coupon Usage
INSERT INTO `coupon_usage` (`id`, `coupon_id`, `customer_id`, `purchase_id`, `discount_applied`, `used_at`) VALUES
(1, 2, 2, 2, 100.00, NOW() - INTERVAL 12 DAY),
(2, 1, 2, 3, 180.00, NOW() - INTERVAL 5 DAY)
ON DUPLICATE KEY UPDATE `id`=VALUES(`id`);
