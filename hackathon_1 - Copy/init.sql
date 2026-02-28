CREATE DATABASE IF NOT EXISTS hackathon_db;
USE hackathon_db;

CREATE TABLE IF NOT EXISTS complaints (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100),
  phone VARCHAR(15), 
  latitude DECIMAL(10,7),
  longitude DECIMAL(10,7),
  priority ENUM('Low','Medium','High','Critical'),
  status ENUM('Pending','Resolved','Social_Notified') DEFAULT 'Pending',
  image_path VARCHAR(255),
  preferred_platform ENUM('Twitter', 'Facebook', 'Instagram') DEFAULT 'Twitter',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
