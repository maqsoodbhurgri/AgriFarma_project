# 🚀 AgriFarma Quick Start Guide

Get AgriFarma up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional)

---

## 🎯 Quick Setup (5 Steps)

### Step 1: Get the Code

**Option A: Clone from GitHub**
```bash
git clone https://github.com/yourusername/agrifarma.git
cd agrifarma
```

**Option B: Download ZIP**
- Download and extract the ZIP file
- Open terminal/command prompt in the extracted folder

---

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install Flask, SQLAlchemy, and all other required packages.

---

### Step 4: Set Up Configuration

**Generate a secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Create .env file:**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Edit .env and set:**
```
SECRET_KEY=<paste-the-generated-key-here>
FLASK_ENV=development
```

---

### Step 5: Initialize Database & Run

```bash
# Initialize database
flask --app app.py init-db

# Create admin user (follow prompts)
flask --app app.py create-admin

# (Optional) Add sample data
flask --app app.py seed-data

# Run the application
python app.py
```

**🎉 Success!** Visit: http://127.0.0.1:5000/

---

## 📝 Default Login Credentials

After creating admin user, use those credentials.

If you ran `seed-data`, test users are:
- **Admin**: admin / password123
- **Farmer**: farmer / password123
- **Consultant**: consultant / password123
- **Vendor**: vendor / password123

⚠️ **Change these passwords in production!**

---

## 🧭 Navigation Guide

### Main Features

1. **Homepage** - `/`
   - Overview of platform features
   - Quick access to all sections

2. **Forum** - `/forum`
   - Browse discussions
   - Create threads
   - Reply to posts

3. **Blog** - `/blog`
   - Read agricultural articles
   - Comment on posts

4. **Consultants** - `/consultancy`
   - Browse expert consultants
   - View profiles and expertise

5. **Marketplace** - `/marketplace`
   - Browse products
   - Add to cart
   - Checkout

6. **Admin Dashboard** - `/analytics/dashboard` (Admin only)
   - View analytics charts
   - Generate reports
   - Manage users

---

## 🎨 User Roles

### Admin
- Full system access
- Analytics dashboard
- User management
- Content moderation

### Farmer
- Create forum posts
- Comment on blogs
- Shop in marketplace
- View own orders

### Consultant
- All Farmer features
- Create consultant profile
- Publish expert articles

### Vendor
- All Farmer features
- Create product listings
- View sales analytics
- Manage inventory

---

## 🛠️ Common Tasks

### Create a New Forum Thread
1. Go to `/forum`
2. Click "New Thread"
3. Select category
4. Enter title and content
5. Click "Post Thread"

### Add Product to Marketplace (Vendor only)
1. Login as vendor
2. Go to `/marketplace/vendor/products`
3. Click "Add Product"
4. Fill in details (name, price, description)
5. Upload image (optional)
6. Click "Save"

### Generate Analytics Report (Admin only)
1. Login as admin
2. Go to `/analytics/dashboard`
3. Select report type (Products, Orders, Revenue)
4. Choose date range
5. Click "Generate Report"
6. Export to CSV/JSON if needed

### Update Profile
1. Click profile icon (top right)
2. Select "Profile"
3. Edit information
4. Upload avatar (optional)
5. Click "Save Changes"

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_analytics.py -v

# With coverage
pytest --cov=agrifarma
```

### Manual Testing
1. Register a new user
2. Login and logout
3. Create forum thread
4. Add product to cart
5. Checkout
6. View analytics (as admin)

---

## 🐛 Troubleshooting

### "No module named 'agrifarma'"
**Solution**: Ensure you're in the project root and virtual environment is activated.

### "Database not found"
**Solution**: Run `flask init-db`

### "ImportError: cannot import name 'db'"
**Solution**: Check if `agrifarma/__init__.py` exists and has `db` defined.

### Static files not loading
**Solution**: 
- Check `static/` folder exists
- Verify `config.py` has correct paths
- Clear browser cache

### Port already in use
**Solution**: 
```bash
# Change port
flask --app app.py run --port 5001

# Or in app.py, change:
app.run(debug=True, port=5001)
```

### CSRF Token Missing
**Solution**: Ensure forms include `{{ form.csrf_token }}`

---

## 📚 Next Steps

### For Development
1. Read [ERROR_HANDLING_DOCUMENTATION.md](ERROR_HANDLING_DOCUMENTATION.md)
2. Review [ANALYTICS_DOCUMENTATION.md](ANALYTICS_DOCUMENTATION.md)
3. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
4. Explore code in `agrifarma/` folder

### For Deployment
1. Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. Run `python deploy_check.py` to verify readiness
3. Choose platform (Render, PythonAnywhere, Heroku)
4. Deploy and test

### For Contribution
1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

---

## 📞 Getting Help

### Documentation
- **README.md** - Full documentation
- **DEPLOYMENT_CHECKLIST.md** - Deployment guide
- **ERROR_HANDLING_DOCUMENTATION.md** - Error handling
- **ANALYTICS_DOCUMENTATION.md** - Analytics features

### Support
- **Email**: support@agrifarma.com
- **GitHub Issues**: Report bugs and request features
- **Stack Overflow**: Use tag [agrifarma]

### Resources
- Flask Documentation: https://flask.palletsprojects.com/
- Bootstrap Docs: https://getbootstrap.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/

---

## ✅ Quick Commands Cheat Sheet

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Database operations
flask --app app.py init-db     # Initialize database
flask db init                   # Initialize migrations
flask db migrate -m "message"  # Create migration
flask db upgrade               # Apply migrations

# User management
flask --app app.py create-admin  # Create admin user

# Data seeding
flask --app app.py seed-data    # Add sample data

# Run application
python app.py                   # Development server
flask --app app.py run          # Alternative
gunicorn app:app                # Production server

# Testing
pytest -v                       # Run all tests
pytest --cov=agrifarma         # With coverage

# Deployment check
python deploy_check.py          # Verify deployment readiness

# Git operations
git add .
git commit -m "message"
git push origin main
```

---

## 🎓 Learning Path

### Beginner
1. ✅ Complete Quick Start (this guide)
2. ✅ Explore the application as different user roles
3. ✅ Read README.md features section
4. ✅ Try creating forum posts and blog comments

### Intermediate
1. ✅ Review code structure in `agrifarma/`
2. ✅ Understand database models in `models/`
3. ✅ Study routes in `routes/`
4. ✅ Run and understand tests

### Advanced
1. ✅ Deploy to production platform
2. ✅ Customize features
3. ✅ Add new modules
4. ✅ Contribute to project

---

## 🌟 Tips & Best Practices

### Development
- ✅ Always activate virtual environment before working
- ✅ Use `.env` for configuration, never hardcode secrets
- ✅ Run tests before committing changes
- ✅ Follow PEP 8 style guide for Python code
- ✅ Write descriptive commit messages

### Security
- ✅ Never commit `.env` file (it's in `.gitignore`)
- ✅ Change default passwords immediately
- ✅ Use HTTPS in production
- ✅ Keep dependencies updated
- ✅ Validate all user inputs

### Performance
- ✅ Use pagination for large datasets
- ✅ Optimize database queries
- ✅ Compress images before upload
- ✅ Enable caching in production
- ✅ Use CDN for static files

---

## 🎉 You're All Set!

You now have AgriFarma running locally. Explore the features, test different user roles, and when ready, follow the deployment guide to publish your application!

**Happy Farming! 🌾**

---

<div align="center">

[Back to README](README.md) | [Deployment Guide](DEPLOYMENT_CHECKLIST.md) | [Documentation](docs/)

</div>
