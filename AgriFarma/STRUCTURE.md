# AgriFarma - Visual Project Structure

```
AgriFarma/
│
├── 📄 app.py                           # Application entry point
├── 📄 config.py                        # Configuration management
├── 📄 requirements.txt                 # Python dependencies
├── 📄 .env.example                     # Environment variables template
├── 📄 .gitignore                       # Git ignore rules
├── 📄 README.md                        # Main documentation
├── 📄 SETUP_GUIDE.md                   # Quick setup guide
├── 📄 PROJECT_SUMMARY.md               # Project overview
├── 📄 setup.bat                        # Windows setup script
├── 📄 run.bat                          # Windows run script
│
├── 📁 agrifarma/                       # Main application package
│   ├── 📄 __init__.py                  # App factory + blueprint registration
│   ├── 📄 extensions.py                # Flask extensions (DB, Login, CSRF, etc.)
│   │
│   ├── 📁 models/                      # Database Models (SQLAlchemy)
│   │   ├── 📄 __init__.py              # Models package
│   │   ├── 📄 base.py                  # Base model with common fields
│   │   ├── 📄 user.py                  # User model (multi-role)
│   │   └── 📄 role.py                  # Role model
│   │
│   ├── 📁 forms/                       # WTForms (with validation)
│   │   ├── 📄 __init__.py              # Forms package
│   │   ├── 📄 auth.py                  # Login, Register, Password forms
│   │   └── 📄 profile.py               # Profile update forms
│   │
│   ├── 📁 routes/                      # Blueprints (URL routing)
│   │   ├── 📄 __init__.py              # Routes package
│   │   ├── 📄 main.py                  # Homepage, dashboard
│   │   ├── 📄 auth.py                  # Login, register, logout
│   │   ├── 📄 admin.py                 # Admin panel
│   │   ├── 📄 forum.py                 # Discussion forum
│   │   ├── 📄 blog.py                  # Knowledge base
│   │   ├── 📄 consultancy.py           # Consultancy services
│   │   └── 📄 marketplace.py           # E-commerce
│   │
│   ├── 📁 services/                    # Business logic layer
│   │   └── 📄 __init__.py              # Services package
│   │
│   └── 📁 templates/                   # Jinja2 HTML Templates
│       ├── 📄 base.html                # Master template (Bootstrap 5)
│       │
│       ├── 📁 main/
│       │   ├── 📄 index.html           # Homepage
│       │   └── 📄 dashboard.html       # User dashboard
│       │
│       ├── 📁 auth/
│       │   ├── 📄 login.html           # Login page
│       │   ├── 📄 register.html        # Registration page
│       │   └── 📄 profile.html         # User profile
│       │
│       ├── 📁 admin/
│       │   └── 📄 dashboard.html       # Admin dashboard
│       │
│       ├── 📁 forum/
│       │   └── 📄 index.html           # Forum homepage
│       │
│       ├── 📁 blog/
│       │   └── 📄 index.html           # Blog homepage
│       │
│       ├── 📁 consultancy/
│       │   └── 📄 index.html           # Consultancy homepage
│       │
│       ├── 📁 marketplace/
│       │   └── 📄 index.html           # Marketplace homepage
│       │
│       └── 📁 errors/
│           ├── 📄 403.html             # Forbidden error
│           ├── 📄 404.html             # Not found error
│           └── 📄 500.html             # Server error
│
└── 📁 static/                          # Static assets
    ├── 📁 css/
    │   ├── 📄 custom.css               # Custom styles
    │   ├── 📄 dark.css                 # (Existing)
    │   └── 📄 style.css                # (Existing)
    │
    ├── 📁 js/
    │   ├── 📄 custom.js                # Custom JavaScript
    │   ├── 📄 dark-mode.js             # (Existing)
    │   └── ... (other existing files)
    │
    ├── 📁 images/                      # (Existing)
    ├── 📁 fonts/                       # (Existing)
    ├── 📁 plugins/                     # (Existing)
    │
    └── 📁 uploads/
        └── 📄 .gitkeep                 # Upload directory placeholder
```

## Color Legend
- 📄 = File
- 📁 = Directory

## Module Status Legend
- ✅ Fully Implemented
- 🔄 Scaffolded (Ready for implementation)
- ⚠️ Needs Configuration

## Component Status

### Backend (Python/Flask)
| Component | Status | Description |
|-----------|--------|-------------|
| App Factory | ✅ | Application initialization complete |
| Extensions | ✅ | DB, Login, CSRF, Bcrypt configured |
| User Model | ✅ | Multi-role user system |
| Role Model | ✅ | Role management |
| Auth Forms | ✅ | Login, Register with validation |
| Profile Forms | ✅ | User profile updates |
| Main Routes | ✅ | Homepage, dashboard |
| Auth Routes | ✅ | Login, register, logout, profile |
| Admin Routes | ✅ | Admin panel with access control |
| Forum Routes | 🔄 | Basic structure ready |
| Blog Routes | 🔄 | Basic structure ready |
| Consultancy Routes | 🔄 | Basic structure ready |
| Marketplace Routes | 🔄 | Basic structure ready |
| CLI Commands | ✅ | init-db, create-admin |
| Config Management | ✅ | Dev/Prod/Test configs |
| Error Handlers | ✅ | 403, 404, 500 handlers |

### Frontend (HTML/CSS/JS)
| Component | Status | Description |
|-----------|--------|-------------|
| Base Template | ✅ | Bootstrap 5 integrated |
| Navigation | ✅ | Responsive navbar |
| Footer | ✅ | Social links, quick links |
| Homepage | ✅ | Feature showcase |
| Login Page | ✅ | Form with validation |
| Register Page | ✅ | Role-specific fields |
| Dashboard | ✅ | User dashboard |
| Profile Page | ✅ | Profile display |
| Admin Dashboard | ✅ | Stats and quick actions |
| Forum Pages | 🔄 | Placeholder ready |
| Blog Pages | 🔄 | Placeholder ready |
| Consultancy Pages | 🔄 | Placeholder ready |
| Marketplace Pages | 🔄 | Placeholder ready |
| Error Pages | ✅ | Custom 403, 404, 500 |
| Custom CSS | ✅ | Brand styling |
| Custom JS | ✅ | Utility functions |

### Database
| Component | Status | Description |
|-----------|--------|-------------|
| SQLite Setup | ✅ | Development database |
| SQLAlchemy ORM | ✅ | Configured |
| Migrations | ✅ | Flask-Migrate ready |
| User Table | ✅ | Multi-role support |
| Role Table | ✅ | Role management |
| Base Model | ✅ | Common fields/methods |

### Security
| Feature | Status | Description |
|---------|--------|-------------|
| Password Hashing | ✅ | Bcrypt implementation |
| CSRF Protection | ✅ | All forms protected |
| Session Security | ✅ | Secure cookies |
| Input Validation | ✅ | WTForms validators |
| SQL Injection Prevention | ✅ | SQLAlchemy ORM |
| XSS Protection | ✅ | Jinja2 auto-escape |
| Role-Based Access | ✅ | Decorators implemented |

## Quick Reference - URL Routes

### Public Routes
```
GET  /                          → Homepage
GET  /auth/login                → Login page
POST /auth/login                → Process login
GET  /auth/register             → Registration page
POST /auth/register             → Process registration
```

### Authenticated Routes
```
GET  /auth/logout               → Logout
GET  /auth/profile              → User profile
GET  /dashboard                 → User dashboard
GET  /forum                     → Forum homepage
GET  /blog                      → Blog homepage
GET  /consultancy               → Consultancy homepage
GET  /marketplace               → Marketplace homepage
```

### Admin Routes (Admin Only)
```
GET  /admin                     → Admin dashboard
GET  /admin/users               → Manage users
GET  /admin/settings            → System settings
```

## Database Schema Overview

### Users Table (Core)
```sql
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
├── full_name
├── phone
├── address, city, province
├── profile_image
├── bio
├── role_id (FK → roles.id)
├── is_active
├── is_verified
├── farm_size, crops_grown, farming_experience (Farmer)
├── specialization, qualifications, consultation_fee (Consultant)
├── business_name, business_license (Vendor)
├── created_at
└── updated_at
```

### Roles Table
```sql
roles
├── id (PK)
├── name (UNIQUE)
├── description
├── created_at
└── updated_at
```

## Technology Stack Summary

**Backend:** Flask 3.0, SQLAlchemy 2.0, Python 3.8+
**Frontend:** Bootstrap 5.3.2, Bootstrap Icons, Custom CSS/JS
**Database:** SQLite (dev), PostgreSQL/MySQL ready
**Security:** Flask-Login, Bcrypt, CSRF Protection
**Forms:** WTForms with validators

## Next Steps Checklist

### Immediate (Ready to Run)
- [ ] Run `setup.bat` or manual setup
- [ ] Execute `flask init-db`
- [ ] Create admin with `flask create-admin`
- [ ] Start server with `flask run`
- [ ] Test at http://127.0.0.1:5000

### Short Term (Feature Implementation)
- [ ] Implement Forum (Topics, Replies)
- [ ] Implement Blog (Posts, Categories, Comments)
- [ ] Implement Consultancy (Bookings)
- [ ] Implement Marketplace (Products, Orders)

### Medium Term (Enhancement)
- [ ] Email verification
- [ ] Password reset
- [ ] Profile image upload
- [ ] Rich text editor for content
- [ ] Search functionality
- [ ] Notifications system

### Long Term (Production)
- [ ] Payment integration
- [ ] Analytics dashboard
- [ ] Mobile API
- [ ] Multi-language support
- [ ] Performance optimization
- [ ] Production deployment

---
**Visual Structure Created:** November 10, 2025
**Status:** Production-Ready Foundation
