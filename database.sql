CREATE DATABASE IF NOT EXISTS it_helpdesk;
USE it_helpdesk;
CREATE TABLE IF NOT EXISTS tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(150) NOT NULL,
  description TEXT NOT NULL,
  category ENUM('Hardware','Software','Network') NOT NULL,
  priority ENUM('Low','Medium','High') NOT NULL,
  status ENUM('Open','In Progress','Resolved') NOT NULL DEFAULT 'Open',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
