CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    create_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_points (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    points INT DEFAULT 0,
    FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE otp_verification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    otp VARCHAR(6) NOT NULL,  
    created TIMESTAMP NOT NULL,
    valid_till TIMESTAMP NOT NULL,
);


CREATE TABLE pending_signups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    email_status VARCHAR(20) CHECK (email_status IN ('verified', 'unverified')) DEFAULT 'unverified'
);

CREATE TABLE points (
    points_code VARCHAR(12) PRIMARY KEY,  
    status VARCHAR(12) CHECK (status IN ('scanned', 'not_scanned')) DEFAULT 'not_scanned',
    points_value INT,
    expiry_date DATE
);

CREATE TABLE scheme (
    scheme_id SERIAL PRIMARY KEY,
    scheme_title VARCHAR(255) NOT NULL,
    scheme_valid_from VARCHAR(12) NOT NULL,
    scheme_valid_to VARCHAR(12),
    scheme_perks TEXT
);

CREATE TABLE schemes_redemption (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    scheme_status VARCHAR(20) CHECK (scheme_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    scheme_id INT REFERENCES scheme(scheme_id)
);

