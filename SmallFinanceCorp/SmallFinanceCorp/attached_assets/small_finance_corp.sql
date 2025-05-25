
-- Small Finance Corporation SQL Schema and Logic

-- Drop if exists (for clean re-run)
DROP TABLE IF EXISTS emi_schedule, loan_audit, repayments, loans, loan_types, customers, users;

-- Customers table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loan types
CREATE TABLE loan_types (
    loan_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    interest_rate DECIMAL(5,2) NOT NULL
);

-- Loans table
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    loan_type_id INT,
    loan_amount DECIMAL(10,2),
    duration_months INT,
    status ENUM('Pending', 'Approved', 'Rejected', 'Closed') DEFAULT 'Pending',
    issue_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (loan_type_id) REFERENCES loan_types(loan_type_id)
);

-- Repayments table
CREATE TABLE repayments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    payment_date DATE,
    amount_paid DECIMAL(10,2),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);

-- Users table (Admin)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin') DEFAULT 'admin'
);

-- EMI Schedule
CREATE TABLE emi_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    customer_id INT,
    emi_amount DECIMAL(10,2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loan Audit table for triggers
CREATE TABLE loan_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View: Active Loans
CREATE VIEW active_loans_view AS
SELECT c.name, l.loan_id, l.loan_amount, lt.type_name
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
JOIN loan_types lt ON l.loan_type_id = lt.loan_type_id
WHERE l.status = 'Approved';

-- Trigger: Audit Loan Status Updates
DELIMITER //
CREATE TRIGGER after_loan_update
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO loan_audit (loan_id, old_status, new_status)
        VALUES (OLD.loan_id, OLD.status, NEW.status);
    END IF;
END;
//
DELIMITER ;

-- Stored Procedure: Calculate EMI for Gold Loans
DELIMITER //
CREATE PROCEDURE calculate_gold_loan_emi()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE lid INT;
    DECLARE cid INT;
    DECLARE lamt DECIMAL(10,2);
    DECLARE rate DECIMAL(5,2);
    DECLARE dur INT;

    DECLARE cur CURSOR FOR
        SELECT l.loan_id, l.customer_id, l.loan_amount, lt.interest_rate, l.duration_months
        FROM loans l
        JOIN loan_types lt ON l.loan_type_id = lt.loan_type_id
        WHERE lt.type_name = 'Gold Loan' AND l.status = 'Approved';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO lid, cid, lamt, rate, dur;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO emi_schedule (loan_id, customer_id, emi_amount)
        VALUES (
            lid, cid,
            ROUND(
                (lamt * rate / 1200 * POW(1 + rate / 1200, dur)) /
                (POW(1 + rate / 1200, dur) - 1),
                2
            )
        );
    END LOOP;

    CLOSE cur;
END;
//
DELIMITER ;
