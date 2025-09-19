CREATE DATABASE IF NOT EXISTS momo_sms
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE momo_sms;

CREATE TABLE users (
  user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(255) DEFAULT NULL,
  national_id VARCHAR(50) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  UNIQUE KEY ux_users_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE categories (
  category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL,
  description VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (category_id),
  UNIQUE KEY ux_categories_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE transactions (
  transaction_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  momo_id VARCHAR(100) DEFAULT NULL,
  sender_id BIGINT UNSIGNED NOT NULL,
  receiver_id BIGINT UNSIGNED NOT NULL,
  amount DECIMAL(13,2) NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'RWF',
  occurred_at DATETIME NOT NULL,
  status ENUM('PENDING','SUCCESS','FAILED','REVERSED') NOT NULL DEFAULT 'PENDING',
  raw_xml TEXT NULL,
  raw_payload JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (transaction_id),
  KEY idx_transactions_occurred_at (occurred_at),
  KEY idx_transactions_amount (amount),
  CONSTRAINT fk_transactions_sender FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_transactions_receiver FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CHECK (amount >= 0),
  CHECK (CHAR_LENGTH(currency) = 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE transaction_category_map (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id BIGINT UNSIGNED NOT NULL,
  category_id INT UNSIGNED NOT NULL,
  assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY ux_tcm_tx_cat (transaction_id, category_id),
  CONSTRAINT fk_tcm_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
  CONSTRAINT fk_tcm_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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

CREATE TABLE system_logs (
  log_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id BIGINT UNSIGNED NULL,
  level VARCHAR(20) NOT NULL,
  source VARCHAR(100) NOT NULL,
  message TEXT NOT NULL,
  logged_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_system_logs_tx (transaction_id),
  CONSTRAINT fk_logs_tx FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (name, phone, email, national_id) VALUES
('Alice Umutesi','250788123456','alice@example.com','100200300'),
('Bob Habimana','250788234567','bob@example.com','100200301'),
('Clement Ntaw','250788345678','clement@example.com',NULL),
('Diane Mukamana','250788456789','diane@example.com','100200302'),
('Eugene Karangwa','250788567890',NULL,NULL);

INSERT INTO categories (code, description) VALUES
('BILL_PAYMENT','Utility bill payment'),
('TRANSFER','Peer-to-peer transfer'),
('AIRTIME_PURCHASE','Buying airtime/topup'),
('MERCHANT_PAYMENT','Payment to merchant'),
('SALARY','Salary payout');

INSERT INTO raw_tags (tag_name) VALUES
('high_value'),('international'),('recurrent'),('promo'),('manual_review');

INSERT INTO transactions (momo_id, sender_id, receiver_id, amount, currency, occurred_at, status, raw_xml, raw_payload) VALUES
('MMO-0001',1,2,5000.00,'RWF','2025-09-01 08:15:00','SUCCESS','<xml>...</xml>',JSON_OBJECT('note','payment for goods','channel','SMS')),
('MMO-0002',2,3,15000.50,'RWF','2025-09-02 09:20:00','SUCCESS','<xml>...</xml>',JSON_OBJECT('note','salary payout','channel','API')),
('MMO-0003',3,4,200.00,'RWF','2025-09-03 10:05:00','FAILED','<xml>...</xml>',JSON_OBJECT('note','airtime purchase','channel','USSD')),
('MMO-0004',4,5,7500.75,'RWF','2025-09-04 15:30:00','PENDING','<xml>...</xml>',JSON_OBJECT('note','merchant payment','channel','WEB')),
('MMO-0005',5,1,12000.00,'RWF','2025-09-05 17:45:00','REVERSED','<xml>...</xml>',JSON_OBJECT('note','refund','channel','SMS'));

INSERT INTO transaction_category_map (transaction_id, category_id) VALUES
(1,2),(1,4),
(2,5),
(3,3),
(4,4),
(5,2);
