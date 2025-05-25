from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Customer, LoanType, Loan, Repayment, EMISchedule, LoanAudit
from forms import CustomerForm, LoanTypeForm, LoanForm, RepaymentForm
from datetime import date
from sqlalchemy import func, text

@app.route('/')
def index():
    """Dashboard with key metrics"""
    try:
        # Get key metrics
        total_customers = Customer.query.count()
        total_loans = Loan.query.count()
        approved_loans = Loan.query.filter_by(status='Approved').count()
        pending_loans = Loan.query.filter_by(status='Pending').count()
        
        # Total loan amount disbursed
        total_disbursed = db.session.query(func.sum(Loan.loan_amount)).filter_by(status='Approved').scalar() or 0
        
        # Total repayments received
        total_repayments = db.session.query(func.sum(Repayment.amount_paid)).scalar() or 0
        
        # Recent loans
        recent_loans = Loan.query.order_by(Loan.loan_id.desc()).limit(5).all()
        
        # Recent repayments
        recent_repayments = Repayment.query.order_by(Repayment.payment_id.desc()).limit(5).all()
        
        return render_template('index.html', 
                             total_customers=total_customers,
                             total_loans=total_loans,
                             approved_loans=approved_loans,
                             pending_loans=pending_loans,
                             total_disbursed=total_disbursed,
                             total_repayments=total_repayments,
                             recent_loans=recent_loans,
                             recent_repayments=recent_repayments)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('index.html', 
                             total_customers=0, total_loans=0, approved_loans=0, 
                             pending_loans=0, total_disbursed=0, total_repayments=0,
                             recent_loans=[], recent_repayments=[])

# Customer routes
@app.route('/customers')
def customers():
    """List all customers"""
    try:
        search = request.args.get('search', '')
        if search:
            customers_list = Customer.query.filter(
                Customer.name.contains(search) | 
                Customer.email.contains(search) |
                Customer.phone.contains(search)
            ).all()
        else:
            customers_list = Customer.query.all()
        return render_template('customers.html', customers=customers_list, search=search)
    except Exception as e:
        flash(f'Error loading customers: {str(e)}', 'danger')
        return render_template('customers.html', customers=[], search='')

@app.route('/customer/new', methods=['GET', 'POST'])
def new_customer():
    """Create new customer"""
    form = CustomerForm()
    if form.validate_on_submit():
        try:
            customer = Customer(
                name=form.name.data,
                email=form.email.data if form.email.data else None,
                phone=form.phone.data,
                address=form.address.data
            )
            db.session.add(customer)
            db.session.commit()
            flash('Customer created successfully!', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating customer: {str(e)}', 'danger')
    
    return render_template('customer_form.html', form=form, title='New Customer')

@app.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    """Edit existing customer"""
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        try:
            customer.name = form.name.data
            customer.email = form.email.data if form.email.data else None
            customer.phone = form.phone.data
            customer.address = form.address.data
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating customer: {str(e)}', 'danger')
    
    return render_template('customer_form.html', form=form, title='Edit Customer', customer=customer)

# Loan Type routes
@app.route('/loan_types')
def loan_types():
    """List all loan types"""
    try:
        loan_types_list = LoanType.query.all()
        return render_template('loan_types.html', loan_types=loan_types_list)
    except Exception as e:
        flash(f'Error loading loan types: {str(e)}', 'danger')
        return render_template('loan_types.html', loan_types=[])

@app.route('/loan_type/new', methods=['GET', 'POST'])
def new_loan_type():
    """Create new loan type"""
    form = LoanTypeForm()
    if form.validate_on_submit():
        try:
            loan_type = LoanType(
                type_name=form.type_name.data,
                interest_rate=form.interest_rate.data
            )
            db.session.add(loan_type)
            db.session.commit()
            flash('Loan type created successfully!', 'success')
            return redirect(url_for('loan_types'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating loan type: {str(e)}', 'danger')
    
    return render_template('loan_type_form.html', form=form, title='New Loan Type')

@app.route('/loan_type/edit/<int:loan_type_id>', methods=['GET', 'POST'])
def edit_loan_type(loan_type_id):
    """Edit existing loan type"""
    loan_type = LoanType.query.get_or_404(loan_type_id)
    form = LoanTypeForm(obj=loan_type)
    
    if form.validate_on_submit():
        try:
            loan_type.type_name = form.type_name.data
            loan_type.interest_rate = form.interest_rate.data
            db.session.commit()
            flash('Loan type updated successfully!', 'success')
            return redirect(url_for('loan_types'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating loan type: {str(e)}', 'danger')
    
    return render_template('loan_type_form.html', form=form, title='Edit Loan Type', loan_type=loan_type)

# Loan routes
@app.route('/loans')
def loans():
    """List all loans"""
    try:
        status_filter = request.args.get('status', '')
        search = request.args.get('search', '')
        
        query = Loan.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if search:
            query = query.join(Customer).filter(
                Customer.name.contains(search) |
                Loan.loan_id.like(f'%{search}%')
            )
        
        loans_list = query.order_by(Loan.loan_id.desc()).all()
        return render_template('loans.html', loans=loans_list, status_filter=status_filter, search=search)
    except Exception as e:
        flash(f'Error loading loans: {str(e)}', 'danger')
        return render_template('loans.html', loans=[], status_filter='', search='')

@app.route('/loan/new', methods=['GET', 'POST'])
def new_loan():
    """Create new loan"""
    form = LoanForm()
    if form.validate_on_submit():
        try:
            loan = Loan(
                customer_id=form.customer_id.data,
                loan_type_id=form.loan_type_id.data,
                loan_amount=form.loan_amount.data,
                duration_months=form.duration_months.data,
                status=form.status.data,
                issue_date=form.issue_date.data if form.issue_date.data else None
            )
            db.session.add(loan)
            db.session.commit()
            
            # If loan is approved, calculate and save EMI
            if loan.status == 'Approved':
                emi_amount = loan.calculate_emi()
                emi_schedule = EMISchedule(
                    loan_id=loan.loan_id,
                    customer_id=loan.customer_id,
                    emi_amount=emi_amount
                )
                db.session.add(emi_schedule)
                db.session.commit()
            
            flash('Loan created successfully!', 'success')
            return redirect(url_for('loans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating loan: {str(e)}', 'danger')
    
    return render_template('loan_form.html', form=form, title='New Loan')

@app.route('/loan/edit/<int:loan_id>', methods=['GET', 'POST'])
def edit_loan(loan_id):
    """Edit existing loan"""
    loan = Loan.query.get_or_404(loan_id)
    form = LoanForm(obj=loan)
    
    if form.validate_on_submit():
        try:
            old_status = loan.status
            loan.customer_id = form.customer_id.data
            loan.loan_type_id = form.loan_type_id.data
            loan.loan_amount = form.loan_amount.data
            loan.duration_months = form.duration_months.data
            loan.status = form.status.data
            loan.issue_date = form.issue_date.data if form.issue_date.data else None
            
            # If status changed to approved, calculate EMI
            if old_status != 'Approved' and loan.status == 'Approved':
                emi_amount = loan.calculate_emi()
                # Check if EMI schedule already exists
                existing_emi = EMISchedule.query.filter_by(loan_id=loan.loan_id).first()
                if not existing_emi:
                    emi_schedule = EMISchedule(
                        loan_id=loan.loan_id,
                        customer_id=loan.customer_id,
                        emi_amount=emi_amount
                    )
                    db.session.add(emi_schedule)
            
            db.session.commit()
            flash('Loan updated successfully!', 'success')
            return redirect(url_for('loans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating loan: {str(e)}', 'danger')
    
    return render_template('loan_form.html', form=form, title='Edit Loan', loan=loan)

# Payment routes
@app.route('/payments')
def payments():
    """List all payments"""
    try:
        loan_id = request.args.get('loan_id', type=int)
        
        query = Repayment.query
        if loan_id:
            query = query.filter_by(loan_id=loan_id)
        
        payments_list = query.order_by(Repayment.payment_date.desc()).all()
        
        # Get loans for filter dropdown
        loans_list = Loan.query.filter_by(status='Approved').all()
        
        return render_template('payments.html', payments=payments_list, loans=loans_list, selected_loan_id=loan_id)
    except Exception as e:
        flash(f'Error loading payments: {str(e)}', 'danger')
        return render_template('payments.html', payments=[], loans=[], selected_loan_id=None)

@app.route('/payment/new', methods=['GET', 'POST'])
def new_payment():
    """Record new payment"""
    form = RepaymentForm()
    if form.validate_on_submit():
        try:
            payment = Repayment(
                loan_id=form.loan_id.data,
                payment_date=form.payment_date.data,
                amount_paid=form.amount_paid.data
            )
            db.session.add(payment)
            db.session.commit()
            flash('Payment recorded successfully!', 'success')
            return redirect(url_for('payments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording payment: {str(e)}', 'danger')
    
    return render_template('payment_form.html', form=form, title='Record Payment')

# EMI Schedule routes
@app.route('/emi_schedule')
def emi_schedule():
    """View EMI schedules"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        
        query = EMISchedule.query
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        schedules = query.order_by(EMISchedule.calculated_at.desc()).all()
        
        # Get customers for filter dropdown
        customers_list = Customer.query.all()
        
        return render_template('emi_schedule.html', schedules=schedules, customers=customers_list, selected_customer_id=customer_id)
    except Exception as e:
        flash(f'Error loading EMI schedules: {str(e)}', 'danger')
        return render_template('emi_schedule.html', schedules=[], customers=[], selected_customer_id=None)

@app.route('/calculate_gold_emi', methods=['POST'])
def calculate_gold_emi():
    """Calculate EMI for all gold loans"""
    try:
        # Execute the stored procedure
        db.session.execute(text('CALL calculate_gold_loan_emi()'))
        db.session.commit()
        flash('Gold loan EMI calculations completed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error calculating gold loan EMI: {str(e)}', 'danger')
    
    return redirect(url_for('emi_schedule'))

# Reports routes
@app.route('/reports')
def reports():
    """Generate reports"""
    try:
        # Loan status distribution
        status_counts = db.session.query(
            Loan.status, 
            func.count(Loan.loan_id).label('count'),
            func.sum(Loan.loan_amount).label('total_amount')
        ).group_by(Loan.status).all()
        
        # Loan type distribution
        type_counts = db.session.query(
            LoanType.type_name,
            func.count(Loan.loan_id).label('count'),
            func.sum(Loan.loan_amount).label('total_amount')
        ).join(Loan).group_by(LoanType.type_name).all()
        
        # Monthly disbursement (last 12 months)
        monthly_disbursement = db.session.query(
            func.date_format(Loan.issue_date, '%Y-%m').label('month'),
            func.sum(Loan.loan_amount).label('amount')
        ).filter(
            Loan.status == 'Approved',
            Loan.issue_date.isnot(None)
        ).group_by(func.date_format(Loan.issue_date, '%Y-%m')).order_by('month').all()
        
        # Top customers by loan amount
        top_customers = db.session.query(
            Customer.name,
            func.count(Loan.loan_id).label('loan_count'),
            func.sum(Loan.loan_amount).label('total_amount')
        ).join(Loan).filter(Loan.status == 'Approved').group_by(Customer.customer_id).order_by(func.sum(Loan.loan_amount).desc()).limit(10).all()
        
        return render_template('reports.html',
                             status_counts=status_counts,
                             type_counts=type_counts,
                             monthly_disbursement=monthly_disbursement,
                             top_customers=top_customers)
    except Exception as e:
        flash(f'Error generating reports: {str(e)}', 'danger')
        return render_template('reports.html',
                             status_counts=[], type_counts=[], 
                             monthly_disbursement=[], top_customers=[])

# API endpoints for AJAX calls
@app.route('/api/loan/<int:loan_id>/emi')
def get_loan_emi(loan_id):
    """Get calculated EMI for a loan"""
    try:
        loan = Loan.query.get_or_404(loan_id)
        emi = loan.calculate_emi()
        return jsonify({'emi': emi, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/customer/<int:customer_id>/loans')
def get_customer_loans(customer_id):
    """Get all loans for a customer"""
    try:
        loans = Loan.query.filter_by(customer_id=customer_id).all()
        loans_data = [{
            'loan_id': loan.loan_id,
            'loan_amount': float(loan.loan_amount),
            'status': loan.status,
            'loan_type': loan.loan_type.type_name
        } for loan in loans]
        return jsonify({'loans': loans_data, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500
