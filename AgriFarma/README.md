# 🌾 AgriFarma – Smart Agriculture Platform

> Empowering farmers through technology

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com)

## 📋 Overview

**AgriFarma** is a comprehensive digital platform designed to empower farmers in Sindh, Pakistan, and beyond. It provides a centralized hub for agricultural knowledge sharing, expert consultation, product marketplace, and community engagement.

### 🎯 Purpose

AgriFarma bridges the gap between traditional farming practices and modern agricultural technology by providing:
- 💬 A knowledge-sharing community forum
- 👨‍🌾 Access to agricultural experts and consultants
- 🛒 An e-commerce marketplace for farming products
- 📊 Data-driven insights through analytics and reporting
- 📚 Educational resources through blogs and articles

### 👥 Target Users

- **Farmers**: Small to large-scale farmers seeking knowledge and resources
- **Agricultural Consultants**: Experts providing guidance and consultation services
- **Vendors**: Agricultural product and equipment suppliers
- **Administrators**: Platform managers and content moderators

---

## ✨ Key Features

### 🔐 User Management
- ✅ Secure registration with email validation
- ✅ Role-based access control (Admin, Farmer, Consultant, Vendor)
- ✅ Profile management with avatar upload
- ✅ Password reset functionality
- ✅ Session management with remember-me option

### 💬 Community Forum
- ✅ Category-based discussions (Crops, Livestock, Equipment)
- ✅ Thread creation and replies
- ✅ Search and filtering
- ✅ Pinned and locked threads
- ✅ Solution marking for resolved issues
- ✅ Admin moderation tools

### 📝 Blog System
- ✅ Create and publish agricultural articles
- ✅ Rich text editor support
- ✅ Image uploads
- ✅ Category tags
- ✅ Comment system

### 👨‍🌾 Consultant Directory
- ✅ Browse experts by expertise
- ✅ Consultant profiles and credentials
- ✅ Rating and review system
- ✅ Book consultation appointments

### 🛒 E-Commerce Marketplace
- ✅ Product catalog with categories
- ✅ Advanced search and filtering
- ✅ Shopping cart functionality
- ✅ Order management
- ✅ Vendor dashboard

### 📊 Admin Dashboard & Analytics
- ✅ Interactive Chart.js visualizations
- ✅ Product sales analytics
- ✅ Order trend analysis
- ✅ Export to CSV/JSON
- ✅ Date range filtering
- ✅ User management tools

### 🎨 Additional Features
- ✅ Flash messaging system with icons
- ✅ Custom error pages (404, 403, 500)
- ✅ Responsive Bootstrap 5 design
- ✅ Dark mode support
- ✅ Mobile-first approach

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.0.0 | Web framework |
| SQLAlchemy | 2.0.23 | Database ORM |
| Flask-Login | 0.6.3 | Authentication |
| Flask-Bcrypt | 1.0.1 | Password hashing |
| Flask-WTF | 1.2.1 | Form handling |
| Pandas | 2.1.4 | Data analysis |

### Frontend
| Technology | Purpose |
|------------|---------|
| Bootstrap 5.3 | CSS framework |
| Chart.js 3.9.1 | Data visualization |
| Feather Icons | Iconography |
| Datta Able Template | Admin theme |

### Development & Deployment
- **Testing**: pytest 7.4.3, pytest-cov 4.1.0
- **Server**: Gunicorn 21.2.0
- **Platforms**: Render, PythonAnywhere, Heroku

---

## 📦 Installation Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/agrifarma.git
cd agrifarma

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY

# 5. Initialize database
flask --app app.py init-db

# 6. Create admin user
flask --app app.py create-admin

# 7. (Optional) Seed sample data
flask --app app.py seed-data

# 8. Run application
python app.py
```

Visit: **http://127.0.0.1:5000/**

### Generate SECRET_KEY

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Deployment

### Deploy to Render.com

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Set environment variables:
   ```
   SECRET_KEY=your-secret-key
   FLASK_ENV=production
   ```
5. Deploy!

### Deploy to PythonAnywhere

```bash
# 1. Upload code to PythonAnywhere

# 2. Create virtual environment
mkvirtualenv --python=/usr/bin/python3.8 agrifarma
pip install -r requirements.txt

# 3. Configure WSGI file (use wsgi.py)

# 4. Set static files mapping
URL: /static/
Directory: /path/to/agrifarma/static/

# 5. Initialize database
flask init-db

# 6. Reload web app
```

### Deploy to Heroku

```bash
# 1. Create app
heroku create your-app-name

# 2. Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# 3. Set config
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV=production

# 4. Deploy
git push heroku main

# 5. Initialize database
heroku run flask init-db
```

---

## 📸 Screenshots

### 🏠 Homepage
Clean and intuitive landing page with navigation to all features

![Homepage](screenshots/homepage.png)

### 📊 Admin Analytics Dashboard
Comprehensive analytics with interactive Chart.js visualizations

![Analytics](screenshots/analytics.png)

### 💬 Community Forum
Active community discussions organized by categories

![Forum](screenshots/forum.png)

### 🛒 Marketplace
E-commerce platform for agricultural products

![Marketplace](screenshots/marketplace.png)

### 👨‍🌾 Consultant Directory
Browse and connect with agricultural experts

![Consultants](screenshots/consultants.png)

### 📱 Mobile Responsive
Mobile-first design works seamlessly on all devices

![Mobile](screenshots/mobile.png)

---

## 📁 Project Structure

```
AgriFarma/
├── agrifarma/                # Main application package
│   ├── __init__.py          # App factory
│   ├── extensions.py        # Flask extensions
│   ├── models/              # Database models
│   │   ├── user.py         # User, Role
│   │   ├── product.py      # Product, Order, OrderItem
│   │   ├── forum.py        # Forum models
│   │   ├── blog.py         # Blog models
│   │   └── consultant.py   # Consultant models
│   ├── routes/              # Blueprints
│   │   ├── auth.py         # Authentication
│   │   ├── admin.py        # Admin panel
│   │   ├── forum.py        # Forum
│   │   ├── blog.py         # Blog
│   │   ├── marketplace.py  # E-commerce
│   │   └── analytics.py    # Reports
│   ├── utils/               # Utilities
│   │   └── decorators.py   # Access control
│   └── forms/               # WTForms
├── templates/               # Jinja2 templates
│   ├── layouts/            # Base layouts
│   ├── errors/             # Error pages
│   ├── analytics/          # Analytics views
│   └── ...
├── static/                  # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   └── plugins/
├── tests/                   # Test suite (46 tests)
├── app.py                   # Entry point
├── config.py                # Configuration
├── wsgi.py                  # Production WSGI
├── requirements.txt         # Dependencies
├── Procfile                 # Render/Heroku config
└── README.md               # This file
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest -v

# With coverage
pytest --cov=agrifarma --cov-report=html

# Specific module
pytest tests/test_analytics.py -v
```

### Test Coverage
- ✅ **Analytics**: 24 tests (dashboard, reports, exports)
- ✅ **Error Handling**: 22 tests (pages, flash, access control)
- ✅ **Total**: 46 automated tests

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Profile management
- [ ] Forum threads and replies
- [ ] Blog posts and comments
- [ ] Product browsing and cart
- [ ] Checkout process
- [ ] Admin analytics
- [ ] Report generation
- [ ] Role-based access
- [ ] Error pages
- [ ] Mobile responsiveness

---

## 🔒 Security

### Authentication & Authorization
- ✅ Bcrypt password hashing
- ✅ Role-based access control (RBAC)
- ✅ Flask-Login session management
- ✅ CSRF protection on forms
- ✅ Secure session cookies

### Data Protection
- ✅ SQLAlchemy ORM (SQL injection prevention)
- ✅ Jinja2 auto-escaping (XSS protection)
- ✅ WTForms input validation
- ✅ File upload restrictions
- ✅ Environment variable configuration

### Error Handling
- ✅ Custom error pages (no stack traces)
- ✅ Database transaction rollback
- ✅ Graceful degradation
- ✅ User-friendly messages

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, analytics, moderation |
| **Farmer** | Forum, blog reading, marketplace shopping, profile management |
| **Consultant** | Farmer permissions + profile creation, expert articles |
| **Vendor** | Farmer permissions + product listings, sales analytics |

---

## 📊 Database Schema

### Core Tables
- `users` - User accounts and authentication
- `roles` - User role definitions
- `products` - Marketplace products
- `orders` - Customer orders
- `order_items` - Order line items
- `forum_categories` - Discussion categories
- `forum_threads` - Discussion threads
- `forum_replies` - Thread replies
- `blog_posts` - Blog articles
- `consultants` - Consultant profiles

---

## 🎨 Design

### Color Scheme
| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #28a745 | Success, agriculture theme |
| Secondary | #17a2b8 | Info, links |
| Danger | #dc3545 | Errors, warnings |
| Warning | #ffc107 | Cautions |
| Dark | #1a2332 | Backgrounds |

### Typography
- **Primary**: Roboto (Sans-serif)
- **Headings**: Poppins (Sans-serif)
- **Code**: Fira Code (Monospace)

---

## 📝 CLI Commands

```bash
# Initialize database
flask --app app.py init-db

# Create admin user
flask --app app.py create-admin

# Seed sample data
flask --app app.py seed-data

# Run development server
flask --app app.py run

# Run with debugging
flask --app app.py run --debug

# Database migrations
flask db init
flask db migrate -m "Migration message"
flask db upgrade
```

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Real-time chat for consultations
- [ ] Mobile app (React Native)
- [ ] Weather API integration
- [ ] AI crop disease detection
- [ ] Multi-language support (Urdu, Sindhi)
- [ ] Payment gateway integration
- [ ] SMS notifications
- [ ] Advanced ML analytics

### Version 1.5 (Near Future)
- [ ] Email notifications
- [ ] Two-factor authentication
- [ ] Enhanced search
- [ ] User messaging system
- [ ] Product reviews and ratings
- [ ] Wishlist functionality

---

## 🙏 Acknowledgments

### Team
- **Project Lead**: [Your Name]
- **Developers**: [Team Members]
- **UI/UX Designer**: [Designer Name]

### Mentors
- **Technical Mentor**: [Mentor Name]
- **Agricultural Expert**: [Expert Name]

### Technologies
- Flask Documentation
- Bootstrap
- Chart.js
- Datta Able Template
- Feather Icons
- Stack Overflow Community

### Special Thanks
- Sindh Agriculture Department
- Local farming communities
- Beta testers and contributors

---

## 📧 Contact

- **Email**: support@agrifarma.com
- **Website**: https://agrifarma.onrender.com
- **GitHub**: https://github.com/yourusername/agrifarma
- **Issues**: [Report a bug](https://github.com/yourusername/agrifarma/issues)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 AgriFarma Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 📚 Documentation

For detailed documentation, see:
- [Error Handling Guide](ERROR_HANDLING_DOCUMENTATION.md)
- [Analytics Documentation](ANALYTICS_DOCUMENTATION.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)

---

## ⭐ Support This Project

If you find AgriFarma helpful:
- ⭐ Star this repository
- 🐛 Report bugs
- 💡 Suggest features
- 🤝 Contribute code
- 📢 Share with others

---

<div align="center">

### Built with ❤️ by the AgriFarma Team

*Empowering farmers through technology*

🌾 **© 2025 AgriFarma. All rights reserved.**

[Website](https://agrifarma.onrender.com) • [Documentation](docs/) • [GitHub](https://github.com/yourusername/agrifarma)

</div>
