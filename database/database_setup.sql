CREATE DATABASE IF NOT EXISTS momo_sms;
USE momo_sms;

-- USERS table
CREATE TABLE users (
  user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'PK - internal user id',
  name VARCHAR(200) NOT NULL COMMENT 'Customer full name',
  phone VARCHAR(20) NOT NULL COMMENT 'E.164 or local phone number',
  email VARCHAR(255) DEFAULT NULL COMMENT 'Optional email',
  national_id VARCHAR(50) DEFAULT NULL COMMENT 'Government ID if available',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
  PRIMARY KEY (user_id),
  UNIQUE KEY ux_users_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CATEGORIES table
CREATE TABLE categories (
  category_id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'PK - category id',
  code VARCHAR(50) NOT NULL COMMENT 'Short code e.g. BILL_PAYMENT, TRANSFER',
  description VARCHAR(255) DEFAULT NULL COMMENT 'Human-readable description',
  PRIMARY KEY (category_id),
  UNIQUE KEY ux_categories_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TRANSACTIONS table
CREATE TABLE transactions (
  transaction_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'PK - internal transaction id',
  momo_id VARCHAR(100) DEFAULT NULL COMMENT 'Provider transaction id from MoMo',
  sender_id BIGINT UNSIGNED NOT NULL COMMENT 'FK -> users.user_id (sender)',
  receiver_id BIGINT UNSIGNED NOT NULL COMMENT 'FK -> users.user_id (receiver)',
  amount DECIMAL(13,2) NOT NULL COMMENT 'Amount transferred',
  currency VARCHAR(3) NOT NULL DEFAULT 'RWF' COMMENT 'ISO currency code',
  occurred_at DATETIME NOT NULL COMMENT 'When transaction happened',
  status ENUM('PENDING','SUCCESS','FAILED','REVERSED') NOT NULL DEFAULT 'PENDING' COMMENT 'Transaction state',
  raw_xml TEXT NULL COMMENT 'Original XML message payload',
  raw_payload JSON NULL COMMENT 'Parsed JSON representation',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Inserted into DB',
  PRIMARY KEY (transaction_id),
  KEY idx_transactions_occurred_at (occurred_at),
  KEY idx_transactions_amount (amount),
  CONSTRAINT fk_transactions_sender FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_transactions_receiver FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CHECK (amount >= 0),
  CHECK (CHAR_LENGTH(currency) BETWEEN 3 AND 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Junction table: transaction_category_map (many-to-many)
CREATE TABLE transaction_category_map (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'PK for junction',
  transaction_id BIGINT UNSIGNED NOT NULL COMMENT 'FK -> transactions',
  category_id INT UNSIGNED NOT NULL COMMENT 'FK -> categories',
  assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When category assigned',
  PRIMARY KEY (id),
  UNIQUE KEY ux_tcm_tx_cat (transaction_id, category_id),
  CONSTRAINT fk_tcm_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
  CONSTRAINT fk_tcm_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tags (optional flexibility)
CREATE TABLE raw_tags (
  tag_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  tag_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (tag_id),
  UNIQUE KEY ux_tag_name (tag_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE transaction_tags (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id BIGINT UNSIGNED NOT NULL,
  tag_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY ux_ttags_tx_tag (transaction_id, tag_id),
  CONSTRAINT fk_ttags_tx FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
  CONSTRAINT fk_ttags_tag FOREIGN KEY (tag_id) REFERENCES raw_tags(tag_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SYSTEM_LOGS table
CREATE TABLE system_logs (
  log_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'PK - log id',
  transaction_id BIGINT UNSIGNED NULL COMMENT 'Optional link to a transaction',
  level VARCHAR(20) NOT NULL COMMENT 'INFO, WARN, ERROR, DEBUG',
  source VARCHAR(100) NOT NULL COMMENT 'Module or service name',
  message TEXT NOT NULL COMMENT 'Log message body',
  logged_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When the log was produced',
  PRIMARY KEY (log_id),
  KEY idx_system_logs_tx (transaction_id),
  CONSTRAINT fk_logs_tx FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample data: users (5)
INSERT INTO users (name, phone, email, national_id) VALUES
('Alice Umutesi','250788123456','alice@example.com','100200300'),
('Bob Habimana','250788234567','bob@example.com','100200301'),
('Clement Ntaw','250788345678','clement@example.com',NULL),
('Diane Mukamana','250788456789','diane@example.com','100200302'),
('Eugene Karangwa','250788567890',NULL,NULL);

-- Sample data: categories (5)
INSERT INTO categories (code, description) VALUES
('BILL_PAYMENT','Utility bill payment'),
('TRANSFER','Peer-to-peer transfer'),
('AIRTIME_PURCHASE','Buying airtime/topup'),
('MERCHANT_PAYMENT','Payment to merchant'),
('SALARY','Salary payout');

-- Sample data: raw_tags
INSERT INTO raw_tags (tag_name) VALUES
('high_value'),('international'),('recurrent'),('promo'),('manual_review');

-- Sample transactions (5)
INSERT INTO transactions (momo_id, sender_id, receiver_id, amount, currency, occurred_at, status, raw_xml, raw_payload) VALUES
('MMO-0001',1,2,5000.00,'RWF','2025-09-01 08:15:00','SUCCESS', '<xml>...</xml>', JSON_OBJECT('note','payment for goods','channel','SMS')),
('MMO-0002',2,3,15000.50,'RWF','2025-09-02 09:20:00','SUCCESS','<xml>...</xml>', JSON_OBJECT('note','salary payout','channel','API')),
('MMO-0003',3,4,200.00,'RWF','2025-09-03 10:05:00','FAILED','<xml>...</xml>', JSON_OBJECT('note','airtime purchase','channel','USSD')),
('MMO-0004',4,5,7500.75,'RWF','2025-09-04 15:30:00','PENDING','<xml>...</xml>', JSON_OBJECT('note','merchant payment','channel','WEB')),
('MMO-0005',5,1,12000.00,'RWF','2025-09-05 17:45:00','REVERSED','<xml>...</xml>', JSON_OBJECT('note','refund','channel','SMS'));

-- Map categories to transactions (many-to-many)
INSERT INTO transaction_category_map (transaction_id, category_id) VALUES
(1,2),(1,4), -- transaction 1: TRANSFER + MERCHANT_PAYMENT
(2,5),      -- transaction 2: SALARY
(3,3),      -- transaction 3: AIRTIME_PURCHASE
(4,4),      -- transaction 4: MERCHANT_PAYMENT
(5,2);      -- transaction 5: TRANS
