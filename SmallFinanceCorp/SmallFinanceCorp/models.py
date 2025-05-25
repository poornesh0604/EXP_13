from app import db
from datetime import datetime, date
from decimal import Decimal

class Customer(db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    loans = db.relationship('Loan', backref='customer', lazy=True)
    emi_schedules = db.relationship('EMISchedule', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class LoanType(db.Model):
    __tablename__ = 'loan_types'
    
    loan_type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False, unique=True)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    
    # Relationships
    loans = db.relationship('Loan', backref='loan_type', lazy=True)
    
    def __repr__(self):
        return f'<LoanType {self.type_name}>'

class Loan(db.Model):
    __tablename__ = 'loans'
    
    loan_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    loan_type_id = db.Column(db.Integer, db.ForeignKey('loan_types.loan_type_id'), nullable=False)
    loan_amount = db.Column(db.Numeric(10, 2))
    duration_months = db.Column(db.Integer)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected', 'Closed', name='loan_status'), default='Pending')
    issue_date = db.Column(db.Date)
    
    # Relationships
    repayments = db.relationship('Repayment', backref='loan', lazy=True)
    emi_schedules = db.relationship('EMISchedule', backref='loan', lazy=True)
    audit_logs = db.relationship('LoanAudit', backref='loan', lazy=True)
    
    def __repr__(self):
        return f'<Loan {self.loan_id}>'
    
    def calculate_emi(self):
        """Calculate EMI using the standard formula"""
        if not self.loan_amount or not self.duration_months or not self.loan_type.interest_rate:
            return 0
        
        principal = float(self.loan_amount)
        rate = float(self.loan_type.interest_rate) / 1200  # Monthly rate
        months = self.duration_months
        
        if rate == 0:
            return principal / months
        
        emi = (principal * rate * pow(1 + rate, months)) / (pow(1 + rate, months) - 1)
        return round(emi, 2)

class Repayment(db.Model):
    __tablename__ = 'repayments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.loan_id'), nullable=False)
    payment_date = db.Column(db.Date)
    amount_paid = db.Column(db.Numeric(10, 2))
    
    def __repr__(self):
        return f'<Repayment {self.payment_id}>'

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', name='user_role'), default='admin')
    
    def __repr__(self):
        return f'<User {self.username}>'

class EMISchedule(db.Model):
    __tablename__ = 'emi_schedule'
    
    schedule_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.loan_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    emi_amount = db.Column(db.Numeric(10, 2))
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EMISchedule {self.schedule_id}>'

class LoanAudit(db.Model):
    __tablename__ = 'loan_audit'
    
    audit_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.loan_id'), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LoanAudit {self.audit_id}>'
