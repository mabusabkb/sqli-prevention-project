-- phpMyAdmin SQL Dump (trimmed to the `user_db` database used by this app)
-- Original export also contained unrelated local databases (bwapp, phpmyadmin,
-- test) which have been removed — they weren't part of this project.
--
-- Seed accounts below are DEMO DATA ONLY (plaintext passwords on purpose, to
-- demonstrate connection.php's one-time migration to bcrypt on first login).
-- Do not reuse these credentials anywhere real.

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS `user_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `user_db`;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(200) NOT NULL,
  `username` varchar(200) NOT NULL,
  `email` varchar(200) NOT NULL,
  `password` varchar(200) NOT NULL,
  `gender` varchar(200) NOT NULL DEFAULT 'Male'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping demo data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `gender`) VALUES
(1, 'admin', 'admin123@gmail.com', 'admin123', 'Male'),
(2, 'shashank', 'shashankghodke3242@gmail.com', 'shashank123', 'Male');

--
-- Indexes for dumped tables
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--
ALTER TABLE `users`
  MODIFY `id` int(200) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

COMMIT;
