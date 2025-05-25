# Small Finance Corporation Management System

A comprehensive Flask-based web application for managing small finance corporation operations including customer management, loan processing, EMI calculations, and payment tracking.

## Features

- **Customer Management**: Add, edit, and manage customer information
- **Loan Types**: Configure different loan types with varying interest rates
- **Loan Processing**: Create, approve, and track loan applications
- **EMI Calculator**: Automatic EMI calculations based on loan amount, rate, and duration
- **Payment Tracking**: Record and monitor customer payments
- **Reports & Analytics**: Dashboard with key metrics and insights
- **Responsive Design**: Mobile-friendly interface with Bootstrap dark theme

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, JavaScript
- **Forms**: Flask-WTF, WTForms
- **Server**: Gunicorn

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd small-finance-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DATABASE_URL="your_postgresql_connection_string"
export SESSION_SECRET="your_secret_key"
```

4. Run the application:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Usage

1. **Setup Loan Types**: Configure loan products with interest rates
2. **Add Customers**: Register customer information
3. **Create Loans**: Process loan applications with automatic EMI calculation
4. **Record Payments**: Track customer payments and loan progress
5. **Monitor Dashboard**: View analytics and key performance metrics

## Database Schema

The system includes the following main entities:
- Customers
- Loan Types
- Loans
- Payments (Repayments)
- EMI Schedules
- Audit Logs

## Security Features

- Form validation and CSRF protection
- Secure password handling
- Environment-based configuration
- SQL injection prevention through ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the GitHub repository.