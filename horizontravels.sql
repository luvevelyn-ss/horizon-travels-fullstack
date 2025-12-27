-- Create and use the database
CREATE DATABASE IF NOT EXISTS horizon_travels;
USE horizon_travels;

UPDATE bookings SET status = 'confirmed' WHERE status IS NULL;

-- 1) Users table
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- 2) Admins table
CREATE TABLE IF NOT EXISTS admins (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    email    VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- 3) Master list of cities
CREATE TABLE IF NOT EXISTS cities (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
);

-- Seed cities
INSERT IGNORE INTO cities (name) VALUES
  ('Aberdeen'), ('Birmingham'), ('Bristol'), ('Cardiff'),
  ('Dundee'), ('Edinburgh'), ('Glasgow'), ('London'),
  ('Manchester'), ('Newcastle'), ('Portsmouth'), ('Southampton');

-- 4) Base fares for each route
CREATE TABLE IF NOT EXISTS base_fares (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    from_city_id   INT NOT NULL,
    to_city_id     INT NOT NULL,
    fare           DECIMAL(10,2) NOT NULL,
    UNIQUE KEY uk_route (from_city_id,to_city_id),
    FOREIGN KEY (from_city_id) REFERENCES cities(id),
    FOREIGN KEY (to_city_id)   REFERENCES cities(id)
);

-- Seed base fares
INSERT IGNORE INTO base_fares (from_city_id, to_city_id, fare)
SELECT c1.id, c2.id, bf.base
FROM (
  SELECT 'Dundee', 'Portsmouth', 120 UNION ALL
  SELECT 'Bristol', 'Manchester', 80 UNION ALL
  SELECT 'Bristol', 'Newcastle', 90 UNION ALL
  SELECT 'Bristol', 'Glasgow', 110 UNION ALL
  SELECT 'Bristol', 'London', 80 UNION ALL
  SELECT 'Manchester', 'Southampton', 90 UNION ALL
  SELECT 'Cardiff', 'Edinburgh', 90
) AS bf(a, b, base)
JOIN cities c1 ON c1.name = bf.a
JOIN cities c2 ON c2.name = bf.b;

-- Mirror reverse routes
INSERT IGNORE INTO base_fares (from_city_id, to_city_id, fare)
SELECT to_city_id, from_city_id, fare FROM base_fares;

-- 5) Flight schedule
CREATE TABLE IF NOT EXISTS flights (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    from_city_id   INT NOT NULL,
    to_city_id     INT NOT NULL,
    depart_time    TIME NOT NULL,
    arrive_time    TIME NOT NULL,
    FOREIGN KEY (from_city_id) REFERENCES cities(id),
    FOREIGN KEY (to_city_id)   REFERENCES cities(id)
);

-- Seed flight data
INSERT IGNORE INTO flights (from_city_id,to_city_id,depart_time,arrive_time) VALUES
  ((SELECT id FROM cities WHERE name='Newcastle'),(SELECT id FROM cities WHERE name='Bristol'),'17:45','19:00'),
  ((SELECT id FROM cities WHERE name='Bristol'),(SELECT id FROM cities WHERE name='Newcastle'),'09:00','10:15'),
  ((SELECT id FROM cities WHERE name='Cardiff'),(SELECT id FROM cities WHERE name='Edinburgh'),'07:00','08:30'),
  ((SELECT id FROM cities WHERE name='Bristol'),(SELECT id FROM cities WHERE name='Manchester'),'12:30','13:30'),
  ((SELECT id FROM cities WHERE name='Manchester'),(SELECT id FROM cities WHERE name='Bristol'),'13:20','14:20'),
  ((SELECT id FROM cities WHERE name='Bristol'),(SELECT id FROM cities WHERE name='London'),'07:40','08:20'),
  ((SELECT id FROM cities WHERE name='London'),(SELECT id FROM cities WHERE name='Manchester'),'13:00','14:00'),
  ((SELECT id FROM cities WHERE name='Manchester'),(SELECT id FROM cities WHERE name='Glasgow'),'12:20','13:30'),
  ((SELECT id FROM cities WHERE name='Bristol'),(SELECT id FROM cities WHERE name='Glasgow'),'08:40','09:45'),
  ((SELECT id FROM cities WHERE name='Glasgow'),(SELECT id FROM cities WHERE name='Newcastle'),'14:30','15:45'),
  ((SELECT id FROM cities WHERE name='Newcastle'),(SELECT id FROM cities WHERE name='Manchester'),'16:15','17:05'),
  ((SELECT id FROM cities WHERE name='Manchester'),(SELECT id FROM cities WHERE name='Bristol'),'18:25','19:30'),
  ((SELECT id FROM cities WHERE name='Bristol'),(SELECT id FROM cities WHERE name='Manchester'),'06:20','07:20'),
  ((SELECT id FROM cities WHERE name='Portsmouth'),(SELECT id FROM cities WHERE name='Dundee'),'12:00','14:00'),
  ((SELECT id FROM cities WHERE name='Dundee'),(SELECT id FROM cities WHERE name='Portsmouth'),'10:00','12:00'),
  ((SELECT id FROM cities WHERE name='Edinburgh'),(SELECT id FROM cities WHERE name='Cardiff'),'18:30','20:00'),
  ((SELECT id FROM cities WHERE name='Southampton'),(SELECT id FROM cities WHERE name='Manchester'),'12:00','13:30'),
  ((SELECT id FROM cities WHERE name='Manchester'),(SELECT id FROM cities WHERE name='Southampton'),'19:00','20:30'),
  ((SELECT id FROM cities WHERE name='Birmingham'),(SELECT id FROM cities WHERE name='Newcastle'),'17:00','17:45'),
  ((SELECT id FROM cities WHERE name='Newcastle'),(SELECT id FROM cities WHERE name='Birmingham'),'07:00','07:45'),
  ((SELECT id FROM cities WHERE name='Aberdeen'),(SELECT id FROM cities WHERE name='Portsmouth'),'08:00','09:30');


-- 6) Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL,
    travel_date       DATE NOT NULL,
    return_date       DATE DEFAULT NULL,
    passengers        INT NOT NULL,
    class             ENUM('economy','business') NOT NULL,
    discount_rate     DECIMAL(4,2) NOT NULL DEFAULT 0,
    total_amount      DECIMAL(10,2) NOT NULL,
    flight_id         INT NOT NULL,
    return_flight_id  INT DEFAULT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	status            ENUM('confirmed','cancelled') NOT NULL DEFAULT 'confirmed',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    FOREIGN KEY (return_flight_id) REFERENCES flights(id),
    CHECK (passengers BETWEEN 1 AND 130)
);

-- 7) Booking seats
CREATE TABLE IF NOT EXISTS booking_seats (
    booking_id  INT NOT NULL,
    seat_label  VARCHAR(5) NOT NULL,
    PRIMARY KEY (booking_id, seat_label),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    from_city VARCHAR(100),
    to_city VARCHAR(100),
    travel_date DATE,
    class_type VARCHAR(50),
    seat_numbers TEXT,
    fare DECIMAL(10,2),
    discount DECIMAL(5,2),
    final_amount DECIMAL(10,2),
    duration_minutes INT,
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);