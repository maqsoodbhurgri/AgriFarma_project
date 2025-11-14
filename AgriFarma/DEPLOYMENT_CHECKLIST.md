# 🚀 AgriFarma Deployment Checklist

## Pre-Deployment Tasks

### 1. Code Quality ✅
- [x] All error pages created (404, 403, 500)
- [x] Flash messaging system implemented
- [x] Role-based access control decorators
- [x] Custom error handlers registered
- [ ] Code reviewed and refactored
- [ ] Removed debug statements and print()
- [ ] Optimized database queries
- [ ] Checked for security vulnerabilities

### 2. Testing ✅
- [x] Analytics tests (24 tests) passing
- [x] Error handling tests (22 tests) passing
- [ ] Run all tests: `pytest -v`
- [ ] Test coverage > 80%
- [ ] Manual testing completed
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile responsiveness verified
- [ ] Form validation tested
- [ ] User flows tested (registration → login → shopping → checkout)

### 3. Database ✅
- [x] Database models created
- [x] Migrations generated
- [ ] Run: `flask db init`
- [ ] Run: `flask db migrate -m "Initial migration"`
- [ ] Run: `flask db upgrade`
- [ ] Seed data script tested: `flask seed-data`
- [ ] Admin user creation tested: `flask create-admin`
- [ ] Database backup plan in place

### 4. Configuration ⚙️
- [x] config.py with production settings
- [x] Environment variables documented in .env.example
- [ ] SECRET_KEY generated (run: `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] DATABASE_URL configured for production
- [ ] Debug mode OFF in production
- [ ] CSRF protection enabled
- [ ] Session cookies secure (HTTPS)
- [ ] Email configuration (if applicable)

### 5. Static Files 📦
- [x] CSS files optimized
- [x] JavaScript files working
- [x] Images compressed
- [x] Fonts included
- [ ] CDN links verified (Bootstrap, Chart.js)
- [ ] Static file serving tested
- [ ] Upload folder permissions set

### 6. Dependencies 📋
- [x] requirements.txt updated with all packages
- [x] Gunicorn added for production
- [ ] Verify all dependencies install: `pip install -r requirements.txt`
- [ ] Remove unused dependencies
- [ ] Pin all versions for reproducibility

### 7. Deployment Files 📄
- [x] Procfile created (Render/Heroku)
- [x] wsgi.py created (PythonAnywhere)
- [x] .gitignore configured
- [x] .env.example provided
- [ ] runtime.txt (optional - specify Python version)
- [ ] README.md comprehensive

### 8. Security 🔒
- [ ] All passwords hashed with Bcrypt
- [ ] CSRF tokens on all forms
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection (auto-escaping)
- [ ] File upload validation
- [ ] Rate limiting considered (future)
- [ ] HTTPS enforced in production
- [ ] Secure headers configured

### 9. Documentation 📚
- [x] README.md with installation instructions
- [x] Features documented
- [x] Screenshots prepared
- [x] API endpoints documented (if any)
- [x] Deployment guide included
- [x] Error handling documentation
- [x] Analytics documentation
- [ ] User guide (optional)

### 10. Performance ⚡
- [ ] Database indexes added
- [ ] Query optimization
- [ ] Pagination implemented
- [ ] Image lazy loading
- [ ] Minified CSS/JS (production)
- [ ] Caching strategy (future)
- [ ] CDN for static files (future)

---

## Deployment Steps

### Option 1: Deploy to Render.com

#### Step 1: Prepare Repository
```bash
# Ensure all changes are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Create Render Account
- Visit https://render.com
- Sign up or log in
- Connect GitHub account

#### Step 3: Create Web Service
1. Click "New +" → "Web Service"
2. Connect repository
3. Configure settings:
   - **Name**: agrifarma
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

#### Step 4: Environment Variables
Add in Render dashboard:
```
SECRET_KEY=<your-generated-secret-key>
FLASK_ENV=production
DATABASE_URL=<auto-provided-by-render-or-external>
```

#### Step 5: Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Access your app at: `https://agrifarma.onrender.com`

#### Step 6: Initialize Database
```bash
# Use Render shell or web terminal
flask init-db
flask create-admin
flask seed-data
```

---

### Option 2: Deploy to PythonAnywhere

#### Step 1: Create Account
- Visit https://www.pythonanywhere.com
- Create free account

#### Step 2: Upload Code
```bash
# Option A: Git clone
git clone https://github.com/yourusername/agrifarma.git

# Option B: Upload ZIP
# Upload via Files tab
```

#### Step 3: Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.8 agrifarma
workon agrifarma
pip install -r requirements.txt
```

#### Step 4: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Select "Manual configuration"
4. Choose Python 3.8

#### Step 5: Configure WSGI File
Edit WSGI configuration file:
```python
import sys
import os

project_home = '/home/yourusername/agrifarma'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
```

#### Step 6: Static Files
Add static files mapping:
- URL: `/static/`
- Directory: `/home/yourusername/agrifarma/static/`

#### Step 7: Environment Variables
Create `.env` file:
```bash
cd ~/agrifarma
nano .env
# Add SECRET_KEY, etc.
```

#### Step 8: Initialize Database
```bash
cd ~/agrifarma
workon agrifarma
flask init-db
flask create-admin
flask seed-data
```

#### Step 9: Reload Web App
- Click "Reload" button in Web tab
- Access: `https://yourusername.pythonanywhere.com`

---

### Option 3: Deploy to Heroku

#### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

#### Step 2: Login
```bash
heroku login
```

#### Step 3: Create App
```bash
heroku create agrifarma-app
```

#### Step 4: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

#### Step 5: Set Config Vars
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV=production
```

#### Step 6: Deploy
```bash
git push heroku main
```

#### Step 7: Initialize Database
```bash
heroku run flask init-db
heroku run flask create-admin
heroku run flask seed-data
```

#### Step 8: Open App
```bash
heroku open
```

---

## Post-Deployment Tasks

### 1. Verification ✅
- [ ] Visit deployed URL
- [ ] Test homepage loads
- [ ] Test user registration
- [ ] Test user login
- [ ] Test forum functionality
- [ ] Test marketplace
- [ ] Test admin dashboard
- [ ] Test analytics reports
- [ ] Verify error pages (404, 500)
- [ ] Check mobile responsiveness
- [ ] Test all navigation links
- [ ] Verify images load
- [ ] Check forms submit correctly

### 2. Create Admin Account
```bash
# Via deployment platform terminal
flask create-admin
# Enter admin details
```

### 3. Seed Demo Data
```bash
flask seed-data
# Generates sample products, orders, users
```

### 4. Monitor & Logs
- [ ] Check deployment logs for errors
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure logging
- [ ] Monitor performance
- [ ] Check database connections

### 5. Domain & SSL (Optional)
- [ ] Configure custom domain
- [ ] Enable HTTPS/SSL certificate
- [ ] Update ALLOWED_HOSTS
- [ ] Set SESSION_COOKIE_SECURE=True

### 6. Backups
- [ ] Set up automated database backups
- [ ] Test restore procedure
- [ ] Document backup schedule

---

## Final Submission Checklist

### 1. Code Repository ✅
- [ ] All code committed to GitHub
- [ ] .gitignore configured
- [ ] No sensitive data (passwords, keys) in repo
- [ ] Clean commit history
- [ ] README.md comprehensive

### 2. Documentation 📚
- [x] README.md with:
  - [x] Project description
  - [x] Features list
  - [x] Technology stack
  - [x] Installation instructions
  - [x] Deployment guide
  - [x] Screenshots
  - [x] Team credits
- [x] ERROR_HANDLING_DOCUMENTATION.md
- [x] ANALYTICS_DOCUMENTATION.md
- [x] IMPLEMENTATION_SUMMARY.md

### 3. Screenshots 📸
Capture and add to `screenshots/` folder:
- [ ] Homepage
- [ ] User dashboard
- [ ] Forum page
- [ ] Blog page
- [ ] Marketplace
- [ ] Product detail
- [ ] Shopping cart
- [ ] Admin analytics dashboard
- [ ] Consultant directory
- [ ] User profile
- [ ] Mobile views (2-3 screenshots)

### 4. Video Demo (Optional) 🎥
- [ ] 2-3 minute walkthrough
- [ ] Show key features
- [ ] Upload to YouTube/Drive
- [ ] Add link to README

### 5. Deployment 🚀
- [ ] App deployed and accessible
- [ ] Deployment URL added to README
- [ ] SSL certificate active (HTTPS)
- [ ] Demo data populated
- [ ] Test admin account created

### 6. Testing Results 🧪
- [ ] All tests passing
- [ ] Coverage report generated
- [ ] Manual test cases documented
- [ ] Bug list (if any) documented

### 7. Submission Package 📦
Create ZIP file with:
- [ ] Complete source code
- [ ] README.md
- [ ] Documentation files
- [ ] Screenshots folder
- [ ] requirements.txt
- [ ] .env.example (no actual .env)
- [ ] Test results/coverage report
- [ ] Deployment link document

### File Structure for Submission:
```
agrifarma-submission.zip
├── agrifarma/              # Source code
├── templates/              # All templates
├── static/                 # Static files
├── tests/                  # Test files
├── screenshots/            # UI screenshots
├── docs/                   # Documentation
│   ├── README.md
│   ├── ERROR_HANDLING_DOCUMENTATION.md
│   ├── ANALYTICS_DOCUMENTATION.md
│   └── IMPLEMENTATION_SUMMARY.md
├── requirements.txt
├── config.py
├── app.py
├── wsgi.py
├── Procfile
└── DEPLOYMENT_LINK.txt    # URL to live site
```

---

## Common Issues & Solutions

### Issue: Deployment fails
**Solution**: Check logs for specific error, verify requirements.txt, ensure Python version compatibility

### Issue: Static files not loading
**Solution**: Configure static file mapping, check STATIC_URL and STATIC_ROOT settings

### Issue: Database not initialized
**Solution**: Run `flask init-db` via deployment terminal

### Issue: 500 Internal Server Error
**Solution**: Check logs, verify SECRET_KEY is set, ensure database is accessible

### Issue: Forms not submitting (CSRF error)
**Solution**: Ensure WTF_CSRF_ENABLED=True and forms include {{ form.csrf_token }}

---

## Support & Resources

### Deployment Platforms
- **Render**: https://render.com/docs
- **PythonAnywhere**: https://help.pythonanywhere.com/
- **Heroku**: https://devcenter.heroku.com/

### Flask Resources
- **Documentation**: https://flask.palletsprojects.com/
- **Deployment Guide**: https://flask.palletsprojects.com/en/3.0.x/deploying/

### Community
- **Stack Overflow**: [flask] tag
- **Reddit**: r/flask
- **Discord**: Flask Community

---

## 🎉 Deployment Complete!

Once all checklist items are complete:
1. ✅ Test thoroughly
2. 📸 Capture screenshots
3. 📝 Update README with deployment URL
4. 🎁 Create submission ZIP
5. 🚀 Submit your project!

**Good luck with your deployment! 🌾**
