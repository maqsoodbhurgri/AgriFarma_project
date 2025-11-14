# Quick Start Guide - Enhanced User Management

## Prerequisites
- Python 3.8+
- Flask and dependencies installed (see requirements.txt)
- Database initialized

## Step-by-Step Setup

### 1. Database Migration (IMPORTANT - Must Do First!)

The enhanced User model has many new fields that need to be added to the database.

```bash
# Navigate to project directory
cd c:\Users\hp\Pictures\AgriFarma

# Create migration
flask db migrate -m "Enhanced User model with comprehensive profile fields"

# Apply migration
flask db upgrade
```

### 2. Create Upload Directory

```bash
# Create directory for profile pictures
mkdir static\uploads
```

Or the application will create it automatically on first upload.

### 3. Run the Application

```bash
# Activate virtual environment (if using)
venv\Scripts\activate

# Run development server
python app.py
```

Or use the provided batch file:
```bash
run.bat
```

### 4. Access the Application

Open your browser and navigate to:
- **Homepage:** http://127.0.0.1:5000/
- **Login:** http://127.0.0.1:5000/login
- **Register:** http://127.0.0.1:5000/register

## Testing the New Features

### 1. Register a New User

1. Go to `/register`
2. Fill in the comprehensive registration form:
   - **Basic Info:** Username, Name, Email, Mobile
   - **Location:** City, State, Country
   - **Professional:** Profession, Expertise Level
   - **Role:** Select Farmer/Consultant/Vendor
   - **Role-specific fields will appear dynamically**
   - **Password:** Create a secure password (min 8 chars, letters + numbers)
3. Submit registration
4. You'll be redirected to login

### 2. Login

1. Go to `/login`
2. Enter username/email and password
3. Check "Remember me" (optional)
4. Login successful - redirected to dashboard

### 3. View Profile

1. After login, click on your profile icon
2. Or navigate to `/profile`
3. See all your profile information displayed in cards:
   - Personal Information
   - Location Details
   - Professional Information
   - Role-specific details (Farming/Consultancy/Business)

### 4. Edit Profile

1. From profile page, click "Edit Profile" button
2. Or navigate to `/edit-profile`
3. Update any fields you want:
   - Change your name, mobile, location
   - Update professional information
   - Upload a profile picture
   - Modify role-specific details
4. Click "Submit" to save changes
5. Or click "Cancel" to discard changes

### 5. Change Password

1. From profile page, click "Change Password" button
2. Or navigate to `/change-password`
3. Enter your current password
4. Enter new password (min 8 chars, letters + numbers)
5. Confirm new password
6. Submit to change password

### 6. Forgot Password (Password Reset)

1. From login page, click "Forgot Password" link
2. Or navigate to `/forgot-password`
3. Enter your email address
4. Submit request
5. **Note:** Currently shows token in flash message (for development)
6. Copy the token from the message
7. Navigate to `/reset-password/<paste-token-here>`
8. Enter new password and confirm
9. Submit to reset password
10. Login with new password

## Template Files Reference

### New Templates Created:

**Authentication Pages:**
- `templates/accounts/login_new.html` - Enhanced login page
- `templates/accounts/register_new.html` - Comprehensive registration form
- `templates/accounts/forgot_password.html` - Forgot password page
- `templates/accounts/reset_password.html` - Reset password with token

**Dashboard Pages:**
- `templates/home/profile_new.html` - User profile display
- `templates/home/edit_profile.html` - Edit profile form
- `templates/home/change_password.html` - Change password form

## Common Issues & Solutions

### Issue 1: "No such table: users" or similar database errors

**Solution:** Run database migration:
```bash
flask db upgrade
```

### Issue 2: "Upload folder not found"

**Solution:** Create the upload directory:
```bash
mkdir static\uploads
```

### Issue 3: Profile picture not uploading

**Checks:**
- File size under 16MB? (configured in config.py)
- File format allowed? (jpg, jpeg, png, gif)
- Upload directory exists?
- Permissions correct on upload directory?

### Issue 4: Password validation failing

**Requirements:**
- Minimum 8 characters
- Must contain at least one letter
- Must contain at least one number
- Example: `Password123`

### Issue 5: Mobile number validation failing

**Format:**
- 10-20 characters
- Numbers and common phone characters (+, -, space, parentheses)
- Example: `+92-300-1234567` or `03001234567`

### Issue 6: Templates not showing correct theme

**Check:**
- Templates are using `base.html` or `base-fullscreen.html`
- Static files (CSS/JS) are loading correctly
- Browser cache cleared

## Features Overview

### User Profile Fields:

**Basic Information:**
- Username (unique, alphanumeric + underscore)
- Full Name
- Email (unique)
- Mobile (unique)
- Alternative Phone

**Location:**
- City
- State (default: Sindh)
- Country (default: Pakistan)
- Full Address

**Professional:**
- Profession (Farmer/Academic/Consultant/Other)
- Expertise Level (Expert/Intermediate/Beginner)
- Specialization
- Qualifications
- Bio (max 500 characters)

**Media:**
- Profile Picture (jpg, jpeg, png, gif)

**Status:**
- Role (assigned during registration)
- Verified status
- Active status
- Join Date
- Last Login

**Role-Specific:**
- **Farmers:** Farm Size, Crops Grown, Farming Experience
- **Consultants:** Consultation Fee, Qualifications
- **Vendors:** Business Name, Business License

### Security Features:

✅ Werkzeug password hashing  
✅ CSRF protection on all forms  
✅ Password strength validation  
✅ Secure file upload handling  
✅ Token-based password reset  
✅ Session security (HttpOnly, SameSite)  
✅ Input validation and sanitization  

## Next Steps

### For Development:

1. **Email Integration:**
   - Configure SMTP settings in `.env`
   - Implement email sending for password reset
   - Test email delivery

2. **Testing:**
   - Test all registration scenarios
   - Test profile updates
   - Test file uploads
   - Test password reset flow

3. **Production Preparation:**
   - Set strong SECRET_KEY in production
   - Configure production database (PostgreSQL recommended)
   - Enable HTTPS
   - Set SESSION_COOKIE_SECURE = True

### For Users:

1. **Complete Your Profile:**
   - Add profile picture
   - Fill in all professional information
   - Update location details
   - Add bio and qualifications

2. **Explore Features:**
   - View other farmers/consultants (when implemented)
   - Use discussion forum (when implemented)
   - Browse knowledge base (when implemented)
   - Access consultancy services (when implemented)

## Support

For issues or questions:
- Check `USER_MANAGEMENT_ENHANCEMENT.md` for detailed documentation
- Review `PROJECT_SUMMARY.md` for project overview
- Check `STRUCTURE.md` for file organization

## Version Info

- **Enhancement Version:** 2.0
- **Base Project:** AgriFarma v1.0
- **Theme:** Datta Able Admin Template
- **Framework:** Flask 3.0.0
- **Database:** SQLite (dev) / PostgreSQL (prod ready)

---

**Happy Coding! 🌾**
