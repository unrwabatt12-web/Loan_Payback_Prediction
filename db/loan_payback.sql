-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 27, 2025 at 06:15 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `loan_payback`
--

-- --------------------------------------------------------

--
-- Stand-in structure for view `approval_by_credit_score`
-- (See below for the actual view)
--
CREATE TABLE `approval_by_credit_score` (
`credit_score_range` varchar(19)
,`total_applications` bigint(21)
,`approved` decimal(22,0)
,`rejected` decimal(22,0)
,`approval_rate` decimal(6,2)
);

-- --------------------------------------------------------

--
-- Table structure for table `batch_predictions`
--

CREATE TABLE `batch_predictions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `batch_name` varchar(255) DEFAULT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_size_kb` decimal(10,2) DEFAULT NULL,
  `total_applications` int(11) NOT NULL,
  `approved_applications` int(11) NOT NULL,
  `rejected_applications` int(11) NOT NULL,
  `approval_rate` decimal(5,2) DEFAULT NULL,
  `processed_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `processing_time_seconds` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `batch_predictions`
--

INSERT INTO `batch_predictions` (`id`, `user_id`, `batch_name`, `file_name`, `file_size_kb`, `total_applications`, `approved_applications`, `rejected_applications`, `approval_rate`, `processed_at`, `processing_time_seconds`) VALUES
(13, 4, 'mixed_results_sample.csv', 'mixed_results_sample.csv', 1.02, 10, 8, 2, 80.00, '2025-12-27 16:50:54', 2.82),
(14, 4, 'low_risk_applicants.csv', 'low_risk_applicants.csv', 0.98, 10, 10, 0, 100.00, '2025-12-27 17:08:50', 8.41);

-- --------------------------------------------------------

--
-- Table structure for table `batch_prediction_details`
--

CREATE TABLE `batch_prediction_details` (
  `id` int(11) NOT NULL,
  `batch_id` int(11) NOT NULL,
  `applicant_name` varchar(100) NOT NULL,
  `annual_income` decimal(15,2) NOT NULL,
  `loan_amount` decimal(15,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `debt_to_income_ratio` decimal(5,4) NOT NULL,
  `credit_score` int(11) NOT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `marital_status` varchar(20) DEFAULT NULL,
  `education_level` varchar(50) DEFAULT NULL,
  `employment_status` varchar(50) DEFAULT NULL,
  `loan_purpose` varchar(100) DEFAULT NULL,
  `grade_subgrade` varchar(10) DEFAULT NULL,
  `prediction` tinyint(4) NOT NULL COMMENT '0 = Rejected, 1 = Approved',
  `probability` decimal(5,4) NOT NULL,
  `risk_score` decimal(5,2) DEFAULT NULL,
  `rejection_reasons` text DEFAULT NULL,
  `row_number` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `batch_prediction_details`
--

INSERT INTO `batch_prediction_details` (`id`, `batch_id`, `applicant_name`, `annual_income`, `loan_amount`, `interest_rate`, `debt_to_income_ratio`, `credit_score`, `gender`, `marital_status`, `education_level`, `employment_status`, `loan_purpose`, `grade_subgrade`, `prediction`, `probability`, `risk_score`, `rejection_reasons`, `row_number`) VALUES
(117, 13, 'David Wilson', 8500000.00, 3000000.00, 5.80, 0.2200, 810, 'Male', 'Married', 'PhD', 'Employed', 'Home', 'A1', 1, 0.9632, NULL, NULL, 1),
(118, 13, 'Maria Garcia', 3800000.00, 1800000.00, 14.20, 0.5200, 590, 'Female', 'Married', 'High School', 'Employed', 'Medical', 'F2', 0, 0.4593, NULL, NULL, 2),
(119, 13, 'James Miller', 9500000.00, 4000000.00, 4.90, 0.1800, 790, 'Male', 'Single', 'Master\'s', 'Self-employed', 'Business', 'A2', 1, 0.9865, NULL, NULL, 3),
(120, 13, 'Sophia Davis', 4200000.00, 1200000.00, 11.50, 0.4800, 620, 'Female', 'Single', 'Bachelor\'s', 'Employed', 'Education', 'C1', 1, 0.6118, NULL, NULL, 4),
(121, 13, 'Michael Taylor', 7200000.00, 2500000.00, 7.80, 0.3200, 710, 'Male', 'Divorced', 'Bachelor\'s', 'Employed', 'Car', 'B2', 1, 0.5661, NULL, NULL, 5),
(122, 13, 'Emma Anderson', 5500000.00, 2000000.00, 9.20, 0.3800, 680, 'Female', 'Married', 'Bachelor\'s', 'Employed', 'Debt consolidation', 'C3', 1, 0.6664, NULL, NULL, 6),
(123, 13, 'Daniel Thomas', 4800000.00, 1500000.00, 10.80, 0.4200, 640, 'Male', 'Single', 'High School', 'Unemployed', 'Other', 'D1', 0, 0.0024, NULL, NULL, 7),
(124, 13, 'Olivia Martinez', 6700000.00, 2800000.00, 6.50, 0.2800, 730, 'Female', 'Single', 'Master\'s', 'Employed', 'Home', 'A2', 1, 0.8990, NULL, NULL, 8),
(125, 13, 'William Lee', 8900000.00, 3500000.00, 5.20, 0.2000, 800, 'Male', 'Married', 'PhD', 'Employed', 'Business', 'A1', 1, 0.9904, NULL, NULL, 9),
(126, 13, 'Ava Harris', 5100000.00, 2200000.00, 8.50, 0.3500, 670, 'Female', 'Divorced', 'Bachelor\'s', 'Self-employed', 'Medical', 'B2', 1, 0.7395, NULL, NULL, 10),
(127, 14, 'Steven King', 12000000.00, 5000000.00, 4.20, 0.1500, 850, 'Male', 'Married', 'PhD', 'Employed', 'Home', 'A1', 1, 0.9921, NULL, NULL, 1),
(128, 14, 'Amanda Clark', 9500000.00, 4000000.00, 4.80, 0.1800, 820, 'Female', 'Married', 'Master\'s', 'Employed', 'Business', 'A2', 1, 0.9686, NULL, NULL, 2),
(129, 14, 'Richard Baker', 11000000.00, 4500000.00, 3.90, 0.1200, 840, 'Male', 'Married', 'PhD', 'Self-employed', 'Home', 'A1', 1, 0.9918, NULL, NULL, 3),
(130, 14, 'Jessica Hall', 8800000.00, 3500000.00, 5.50, 0.2000, 800, 'Female', 'Single', 'Master\'s', 'Employed', 'Education', 'A2', 1, 0.9960, NULL, NULL, 4),
(131, 14, 'Thomas Wright', 10500000.00, 4200000.00, 4.50, 0.1400, 830, 'Male', 'Divorced', 'PhD', 'Employed', 'Business', 'A1', 1, 0.9921, NULL, NULL, 5),
(132, 14, 'Melissa Allen', 9200000.00, 3800000.00, 5.20, 0.1900, 810, 'Female', 'Married', 'Master\'s', 'Employed', 'Home', 'A2', 1, 0.9853, NULL, NULL, 6),
(133, 14, 'Charles Young', 9800000.00, 3900000.00, 4.90, 0.1700, 825, 'Male', 'Single', 'PhD', 'Employed', 'Education', 'A1', 1, 0.9888, NULL, NULL, 7),
(134, 14, 'Jennifer King', 10100000.00, 4100000.00, 4.30, 0.1300, 835, 'Female', 'Widowed', 'Master\'s', 'Retired', 'Home', 'A2', 1, 0.9998, NULL, NULL, 8),
(135, 14, 'George Hill', 11500000.00, 4800000.00, 3.70, 0.1100, 845, 'Male', 'Married', 'PhD', 'Employed', 'Business', 'A1', 1, 0.9904, NULL, NULL, 9),
(136, 14, 'Sandra Scott', 9400000.00, 3700000.00, 5.00, 0.1600, 815, 'Female', 'Married', 'Master\'s', 'Employed', 'Car', 'A3', 1, 0.9664, NULL, NULL, 10);

-- --------------------------------------------------------

--
-- Table structure for table `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token` varchar(100) NOT NULL,
  `expires_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_used` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `used_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Stand-in structure for view `recent_predictions_summary`
-- (See below for the actual view)
--
CREATE TABLE `recent_predictions_summary` (
`prediction_type` varchar(6)
,`username` varchar(50)
,`applicant_name` varchar(255)
,`loan_amount` decimal(15,2)
,`credit_score` int(11)
,`prediction` tinyint(4)
,`probability` decimal(5,4)
,`prediction_date` timestamp
);

-- --------------------------------------------------------

--
-- Table structure for table `single_predictions`
--

CREATE TABLE `single_predictions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `applicant_name` varchar(100) NOT NULL,
  `annual_income` decimal(15,2) NOT NULL,
  `loan_amount` decimal(15,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `debt_to_income_ratio` decimal(5,4) NOT NULL,
  `credit_score` int(11) NOT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `marital_status` varchar(20) DEFAULT NULL,
  `education_level` varchar(50) DEFAULT NULL,
  `employment_status` varchar(50) DEFAULT NULL,
  `loan_purpose` varchar(100) DEFAULT NULL,
  `grade_subgrade` varchar(10) DEFAULT NULL,
  `prediction` tinyint(4) NOT NULL COMMENT '0 = Rejected, 1 = Approved',
  `probability` decimal(5,4) NOT NULL,
  `risk_score` decimal(5,2) DEFAULT NULL,
  `rejection_reasons` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `single_predictions`
--

INSERT INTO `single_predictions` (`id`, `user_id`, `applicant_name`, `annual_income`, `loan_amount`, `interest_rate`, `debt_to_income_ratio`, `credit_score`, `gender`, `marital_status`, `education_level`, `employment_status`, `loan_purpose`, `grade_subgrade`, `prediction`, `probability`, `risk_score`, `rejection_reasons`, `created_at`) VALUES
(11, 4, 'MUGABO Patrick', 8500000.00, 3000000.00, 5.80, 0.2200, 810, 'Male', 'Married', 'PhD', 'Employed', 'Home', 'A1', 1, 0.9632, NULL, NULL, '2025-12-27 16:48:49'),
(12, 4, 'Esperance ISHIMWE', 8500000.00, 3000000.00, 5.80, 0.2200, 810, 'Female', 'Married', 'Bachelor\'s', 'Employed', 'Car', 'A1', 1, 0.8839, NULL, NULL, '2025-12-27 17:03:03');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `is_admin` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT 0,
  `reset_token` varchar(255) DEFAULT NULL,
  `reset_token_expiry` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `full_name`, `hashed_password`, `is_active`, `is_admin`, `created_at`, `updated_at`, `last_login`, `is_verified`, `reset_token`, `reset_token_expiry`) VALUES
(1, 'admin', 'admin@gmail.com', 'System Administrator', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 1, 1, '2025-12-19 19:33:57', '2025-12-21 11:53:37', '2025-12-21 10:14:18', 0, 'ESt2Rr8Co7WJNWszImRMN06tf6nIduo1', '2025-12-21 14:53:37'),
(4, 'kalisa', 'kalisa@gmail.com', 'Augustin KALISA', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 1, 0, '2025-12-19 21:08:43', '2025-12-27 17:11:23', '2025-12-27 17:11:23', 0, NULL, NULL),
(5, 'owen', 'kylenowen@yahoo.fr', 'ISHAMI BIGWI Kylen Owen', 'd5c827a582dd116d91c87086e0dfcc1f9746d138b33c876814cc5629008e3485', 1, 0, '2025-12-21 08:24:24', '2025-12-22 11:31:56', '2025-12-22 11:31:56', 0, NULL, NULL),
(6, 'augustin', 'augustin@yahoo.fr', 'Augustin', '7676aaafb027c825bd9abab78b234070e702752f625b752e55e55b48e607e358', 1, 0, '2025-12-21 12:09:35', '2025-12-21 12:09:35', NULL, 0, NULL, NULL);

-- --------------------------------------------------------

--
-- Stand-in structure for view `user_statistics`
-- (See below for the actual view)
--
CREATE TABLE `user_statistics` (
`id` int(11)
,`username` varchar(50)
,`email` varchar(100)
,`full_name` varchar(100)
,`created_at` timestamp
,`last_login` timestamp
,`total_single_predictions` bigint(21)
,`total_batch_predictions` bigint(21)
,`total_applications_processed` decimal(32,0)
,`total_approved` decimal(32,0)
,`total_rejected` decimal(32,0)
);

-- --------------------------------------------------------

--
-- Structure for view `approval_by_credit_score`
--
DROP TABLE IF EXISTS `approval_by_credit_score`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `approval_by_credit_score`  AS SELECT CASE WHEN `combined`.`credit_score` < 580 THEN 'Poor (300-579)' WHEN `combined`.`credit_score` < 670 THEN 'Fair (580-669)' WHEN `combined`.`credit_score` < 740 THEN 'Good (670-739)' WHEN `combined`.`credit_score` < 800 THEN 'Very Good (740-799)' ELSE 'Excellent (800-850)' END AS `credit_score_range`, count(0) AS `total_applications`, sum(case when `combined`.`prediction` = 1 then 1 else 0 end) AS `approved`, sum(case when `combined`.`prediction` = 0 then 1 else 0 end) AS `rejected`, round(avg(case when `combined`.`prediction` = 1 then 1 else 0 end) * 100,2) AS `approval_rate` FROM (select `single_predictions`.`credit_score` AS `credit_score`,`single_predictions`.`prediction` AS `prediction` from `single_predictions` union all select `batch_prediction_details`.`credit_score` AS `credit_score`,`batch_prediction_details`.`prediction` AS `prediction` from `batch_prediction_details`) AS `combined` GROUP BY CASE WHEN `combined`.`credit_score` < 580 THEN 'Poor (300-579)' WHEN `combined`.`credit_score` < 670 THEN 'Fair (580-669)' WHEN `combined`.`credit_score` < 740 THEN 'Good (670-739)' WHEN `combined`.`credit_score` < 800 THEN 'Very Good (740-799)' ELSE 'Excellent (800-850)' END ORDER BY min(`combined`.`credit_score`) ASC ;

-- --------------------------------------------------------

--
-- Structure for view `recent_predictions_summary`
--
DROP TABLE IF EXISTS `recent_predictions_summary`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `recent_predictions_summary`  AS SELECT 'Single' AS `prediction_type`, `u`.`username` AS `username`, `sp`.`applicant_name` AS `applicant_name`, `sp`.`loan_amount` AS `loan_amount`, `sp`.`credit_score` AS `credit_score`, `sp`.`prediction` AS `prediction`, `sp`.`probability` AS `probability`, `sp`.`created_at` AS `prediction_date` FROM (`single_predictions` `sp` join `users` `u` on(`sp`.`user_id` = `u`.`id`))union all select 'Batch' AS `prediction_type`,`u`.`username` AS `username`,`bp`.`file_name` AS `applicant_name`,NULL AS `loan_amount`,NULL AS `credit_score`,NULL AS `prediction`,NULL AS `probability`,`bp`.`processed_at` AS `prediction_date` from (`batch_predictions` `bp` join `users` `u` on(`bp`.`user_id` = `u`.`id`)) order by `prediction_date` desc  ;

-- --------------------------------------------------------

--
-- Structure for view `user_statistics`
--
DROP TABLE IF EXISTS `user_statistics`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `user_statistics`  AS SELECT `u`.`id` AS `id`, `u`.`username` AS `username`, `u`.`email` AS `email`, `u`.`full_name` AS `full_name`, `u`.`created_at` AS `created_at`, `u`.`last_login` AS `last_login`, count(distinct `sp`.`id`) AS `total_single_predictions`, count(distinct `bp`.`id`) AS `total_batch_predictions`, coalesce(sum(`bp`.`total_applications`),0) AS `total_applications_processed`, coalesce(sum(`bp`.`approved_applications`),0) AS `total_approved`, coalesce(sum(`bp`.`rejected_applications`),0) AS `total_rejected` FROM ((`users` `u` left join `single_predictions` `sp` on(`u`.`id` = `sp`.`user_id`)) left join `batch_predictions` `bp` on(`u`.`id` = `bp`.`user_id`)) GROUP BY `u`.`id`, `u`.`username`, `u`.`email`, `u`.`full_name`, `u`.`created_at`, `u`.`last_login` ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `batch_predictions`
--
ALTER TABLE `batch_predictions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_batch_predictions_user_id` (`user_id`),
  ADD KEY `idx_batch_predictions_processed_at` (`processed_at`);

--
-- Indexes for table `batch_prediction_details`
--
ALTER TABLE `batch_prediction_details`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_batch_details_batch_id` (`batch_id`),
  ADD KEY `idx_batch_details_prediction` (`prediction`),
  ADD KEY `idx_batch_details_credit_score` (`credit_score`);

--
-- Indexes for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `idx_reset_tokens_token` (`token`),
  ADD KEY `idx_reset_tokens_user_id` (`user_id`),
  ADD KEY `idx_reset_tokens_expires_at` (`expires_at`);

--
-- Indexes for table `single_predictions`
--
ALTER TABLE `single_predictions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_single_predictions_user_id` (`user_id`),
  ADD KEY `idx_single_predictions_created_at` (`created_at`),
  ADD KEY `idx_single_predictions_prediction` (`prediction`),
  ADD KEY `idx_single_predictions_credit_score` (`credit_score`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_users_username` (`username`),
  ADD KEY `idx_users_email` (`email`),
  ADD KEY `idx_users_created_at` (`created_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `batch_predictions`
--
ALTER TABLE `batch_predictions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `batch_prediction_details`
--
ALTER TABLE `batch_prediction_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=137;

--
-- AUTO_INCREMENT for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `single_predictions`
--
ALTER TABLE `single_predictions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `batch_predictions`
--
ALTER TABLE `batch_predictions`
  ADD CONSTRAINT `batch_predictions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `batch_prediction_details`
--
ALTER TABLE `batch_prediction_details`
  ADD CONSTRAINT `batch_prediction_details_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `batch_predictions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD CONSTRAINT `password_reset_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `single_predictions`
--
ALTER TABLE `single_predictions`
  ADD CONSTRAINT `single_predictions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
