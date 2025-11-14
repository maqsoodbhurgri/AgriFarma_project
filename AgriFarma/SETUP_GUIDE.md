# AgriFarma - Quick Setup Guide

This guide will help you get AgriFarma up and running in minutes.

## Quick Start (Windows)

### 1. Open PowerShell in the AgriFarma directory
```powershell
cd C:\Users\hp\Pictures\AgriFarma
```

### 2. Create and activate virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Set up environment variables
```powershell
# Copy example env file
copy .env.example .env

# Edit .env file and update SECRET_KEY (optional for development)
notepad .env
```

### 5. Initialize the database
```powershell
flask init-db
```

### 6. Create an admin user (optional)
```powershell
flask create-admin
```

Follow the prompts to create your admin account.

### 7. Run the application
```powershell
flask run
```

### 8. Open your browser
Navigate to: `http://127.0.0.1:5000`

## Default Accounts

After running `flask create-admin`, you can create multiple test accounts:

### Test Users You Can Create:
1. **Admin User** - Full system access
   - Created via `flask create-admin` command

2. **Farmer** - Register via web interface
   - Select "Farmer" role during registration
   - Fill in farm-specific fields

3. **Consultant** - Register via web interface
   - Select "Agricultural Consultant" role
   - Provide specialization and qualifications

4. **Vendor** - Register via web interface
   - Select "Product Vendor" role
   - Provide business information

## Testing the Application

### 1. Test User Registration
- Go to http://127.0.0.1:5000/auth/register
- Fill in the form
- Select a role (Farmer/Consultant/Vendor)
- Submit the form

### 2. Test Login
- Go to http://127.0.0.1:5000/auth/login
- Use your credentials
- You'll be redirected to the dashboard

### 3. Explore Features
- **Forum**: http://127.0.0.1:5000/forum
- **Knowledge Base**: http://127.0.0.1:5000/blog
- **Consultancy**: http://127.0.0.1:5000/consultancy
- **Marketplace**: http://127.0.0.1:5000/marketplace
- **Admin Panel**: http://127.0.0.1:5000/admin (admin users only)

## Troubleshooting

### Issue: "No module named 'flask'"
**Solution**: Make sure you activated the virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Issue: Database errors
**Solution**: Reinitialize the database
```powershell
# Delete the existing database
Remove-Item agrifarma.db -ErrorAction SilentlyContinue

# Reinitialize
flask init-db
```

### Issue: Port 5000 already in use
**Solution**: Use a different port
```powershell
flask run --port 5001
```

### Issue: CSRF token errors
**Solution**: Clear your browser cache and cookies, or use incognito mode

## Development Tips

### Using Flask Shell
```powershell
flask shell
```

In the shell, you can interact with the database:
```python
# Get all users
from agrifarma.models.user import User
users = User.query.all()

# Create a user programmatically
from agrifarma.models.role import Role
from agrifarma.extensions import db

role = Role.query.filter_by(name='farmer').first()
user = User(username='testfarmer', email='farmer@test.com', role_id=role.id)
user.set_password('password123')
db.session.add(user)
db.session.commit()
```

### Database Migrations
When you modify models:
```powershell
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply the migration
flask db upgrade
```

### Running in Debug Mode
The application runs in debug mode by default when using `flask run`. 
This enables:
- Auto-reload on code changes
- Detailed error pages
- Debug toolbar (if enabled)

### Viewing Logs
All Flask logs appear in the terminal where you ran `flask run`.

## Next Steps

1. **Customize the application**
   - Modify templates in `agrifarma/templates/`
   - Update styles in `static/css/custom.css`
   - Add custom JavaScript in `static/js/custom.js`

2. **Add new features**
   - Create new models in `agrifarma/models/`
   - Add forms in `agrifarma/forms/`
   - Create routes in `agrifarma/routes/`
   - Design templates in `agrifarma/templates/`

3. **Deploy to production**
   - See README.md for deployment guidelines
   - Configure production database
   - Set up email service
   - Enable HTTPS

## Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Review the README.md file
3. Check Flask documentation: https://flask.palletsprojects.com/

## Project Structure Reference

```
agrifarma/
├── models/          # Database models
├── forms/           # WTForms
├── routes/          # URL routes (blueprints)
├── services/        # Business logic
└── templates/       # HTML templates

static/
├── css/            # Stylesheets
├── js/             # JavaScript
└── uploads/        # User uploads

app.py              # Application entry point
config.py           # Configuration
requirements.txt    # Dependencies
```

Happy coding! 🌾
