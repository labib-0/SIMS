-- ========================================================
-- SIMS (Stock & Inventory Management System) Database Dump
-- Compatible with XAMPP / MariaDB / MySQL / phpMyAdmin
-- ========================================================

CREATE DATABASE IF NOT EXISTS `sims_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `sims_db`;

-- --------------------------------------------------------
-- Table structure for table `users`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` VARCHAR(20) NOT NULL,
  `full_name` VARCHAR(100) NOT NULL,
  `role` VARCHAR(50) NOT NULL,
  `dob` VARCHAR(20) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping default users
INSERT INTO `users` (`user_id`, `full_name`, `role`, `dob`, `email`, `password`) VALUES
('A100', 'Default Admin', 'Admin', '01/01/2000', 'admin@sims.com', '1880291158179'),
('M100', 'Asad', 'Store Manager', '10/10/2000', 'asad@sims.com', '1450576392'),
('S100', 'Masuk', 'Sales Staff', '10/10/2000', 'masuk@sims.com', '1450576392'),
('S101', 'Rim', 'Sales Staff', '10/10/2000', 'rim@sims.com', '1450576392')
ON DUPLICATE KEY UPDATE `user_id`=`user_id`;

-- --------------------------------------------------------
-- Table structure for table `products`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `products` (
  `product_id` VARCHAR(20) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `category` VARCHAR(50) NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `quantity` INT NOT NULL,
  `min_stock` INT NOT NULL,
  `restock_qty` INT DEFAULT 0,
  `stock_alert` VARCHAR(50) DEFAULT '-',
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping default products
INSERT INTO `products` (`product_id`, `name`, `category`, `price`, `quantity`, `min_stock`, `restock_qty`, `stock_alert`) VALUES
('P001', 'Laptop', 'Electronics', 1250.00, 15, 3, 0, '-'),
('P002', 'Mouse', 'Electronics', 29.99, 65, 10, 0, '-'),
('P003', 'Keyboard', 'Electronics', 89.50, 4, 5, 0, 'System Low Stock'),
('P004', 'Monitor', 'Electronics', 340.00, 8, 2, 0, '-'),
('P005', 'Headphones', 'Electronics', 55.00, 0, 5, 0, 'System Out of Stock'),
('P006', 'Hub', 'Electronics', 45.00, 20, 5, 0, '-'),
('P007', 'Rice', 'Groceries', 18.50, 120, 20, 0, '-'),
('P008', 'Milk', 'Groceries', 3.25, 2, 15, 0, 'System Low Stock'),
('P009', 'Oil', 'Groceries', 14.99, 35, 8, 0, '-'),
('P010', 'Chair', 'Furniture', 210.00, 6, 2, 0, '-'),
('P011', 'Desk', 'Furniture', 380.00, 1, 3, 5, 'Staff Reported'),
('P012', 'Bottle', 'Lifestyle', 16.00, 40, 10, 0, '-'),
('P013', 'Purifier', 'Home', 129.00, 0, 4, 10, 'Staff Reported'),
('P014', 'Machine', 'Home', 195.00, 12, 3, 0, '-'),
('P015', 'Paper', 'Stationery', 6.50, 94, 15, 0, '-')
ON DUPLICATE KEY UPDATE `product_id`=`product_id`;

-- --------------------------------------------------------
-- Table structure for table `transactions`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `transactions` (
  `id` INT AUTO_INCREMENT,
  `trans_id` VARCHAR(30) NOT NULL,
  `date` VARCHAR(20) NOT NULL,
  `time` VARCHAR(20) NOT NULL,
  `product_id` VARCHAR(20) NOT NULL,
  `product_name` VARCHAR(100) NOT NULL,
  `quantity` INT NOT NULL,
  `unit_price` DECIMAL(10,2) NOT NULL,
  `total_price` DECIMAL(10,2) NOT NULL,
  `sold_by` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `audit_logs`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` INT AUTO_INCREMENT,
  `timestamp` VARCHAR(30) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  `action` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `audit_logs` (`timestamp`, `user_id`, `action`) VALUES
(NOW(), 'SYSTEM', 'XAMPP MariaDB Database sims_db initialized successfully');
