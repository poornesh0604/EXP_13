from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length
from models import LoanType, Customer

class CustomerForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    address = TextAreaField('Address', validators=[Optional()])

class LoanTypeForm(FlaskForm):
    type_name = StringField('Loan Type Name', validators=[DataRequired(), Length(min=2, max=50)])
    interest_rate = DecimalField('Interest Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], places=2)

class LoanForm(FlaskForm):
    customer_id = SelectField('Customer', validators=[DataRequired()], coerce=int)
    loan_type_id = SelectField('Loan Type', validators=[DataRequired()], coerce=int)
    loan_amount = DecimalField('Loan Amount', validators=[DataRequired(), NumberRange(min=1)], places=2)
    duration_months = IntegerField('Duration (Months)', validators=[DataRequired(), NumberRange(min=1, max=360)])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed')
    ], validators=[DataRequired()])
    issue_date = DateField('Issue Date', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        # Populate choices dynamically
        self.customer_id.choices = [(0, 'Select Customer')] + [(c.customer_id, c.name) for c in Customer.query.all()]
        self.loan_type_id.choices = [(0, 'Select Loan Type')] + [(lt.loan_type_id, f"{lt.type_name} ({lt.interest_rate}%)") for lt in LoanType.query.all()]

class RepaymentForm(FlaskForm):
    loan_id = SelectField('Loan', validators=[DataRequired()], coerce=int)
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    amount_paid = DecimalField('Amount Paid', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    
    def __init__(self, *args, **kwargs):
        super(RepaymentForm, self).__init__(*args, **kwargs)
        from models import Loan
        # Show only approved loans
        approved_loans = Loan.query.filter_by(status='Approved').all()
        self.loan_id.choices = [(0, 'Select Loan')] + [
            (loan.loan_id, f"Loan #{loan.loan_id} - {loan.customer.name} (₹{loan.loan_amount})")
            for loan in approved_loans
        ]
