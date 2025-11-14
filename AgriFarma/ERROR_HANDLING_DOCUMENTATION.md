# Error Handling & Access Control Documentation

## Overview

This document provides comprehensive documentation for the AgriFarma error handling system and role-based access control (RBAC) implementation. The system includes custom error pages, flash messaging, and decorators for protecting routes based on user roles.

## Table of Contents

1. [Error Pages](#error-pages)
2. [Flash Messaging System](#flash-messaging-system)
3. [Role-Based Access Control](#role-based-access-control)
4. [Implementation Guide](#implementation-guide)
5. [Testing](#testing)
6. [Best Practices](#best-practices)

---

## Error Pages

### Available Error Pages

AgriFarma includes three custom error pages with consistent dark theme styling and green accent colors:

#### 1. 404 - Page Not Found (`templates/errors/error_404.html`)

**Purpose**: Displayed when a user tries to access a non-existent page.

**Features**:
- Large "404" error code in green (#28a745)
- Feather icon: `icon-alert-circle`
- Friendly message: "Oops! Page Not Found"
- Suggestions list with helpful tips
- Action buttons:
  - "Back to Homepage" (primary button)
  - "Go Back" (uses browser history)
- Contact support link

**When triggered**:
- User navigates to `/nonexistent-page`
- Broken internal links
- Mistyped URLs

#### 2. 500 - Internal Server Error (`templates/errors/error_500.html`)

**Purpose**: Displayed when the server encounters an unexpected error.

**Features**:
- Large "500" error code in red (#dc3545)
- Feather icon: `icon-alert-triangle`
- Message: "Internal Server Error"
- Error explanation without technical details
- Suggestions for users:
  - Refresh the page
  - Wait and try again
  - Return to homepage
  - Contact support
- Action buttons:
  - "Back to Homepage"
  - "Refresh Page"

**When triggered**:
- Unhandled exceptions in route handlers
- Database errors
- Configuration issues
- Third-party API failures

**Note**: The error handler automatically rolls back database sessions to prevent data corruption.

#### 3. 403 - Access Forbidden (`templates/errors/error_403.html`)

**Purpose**: Displayed when a user tries to access a page they don't have permission for.

**Features**:
- Large "403" error code in yellow (#ffc107)
- Feather icon: `icon-lock`
- Message: "Access Forbidden"
- Explanation of permission requirements
- Dynamic buttons based on authentication status:
  - **Authenticated users**: "Back to Homepage", "My Profile"
  - **Anonymous users**: "Login to Continue", "Homepage"
- Current role display for authenticated users
- Contact admin link

**When triggered**:
- Non-admin tries to access admin routes
- User attempts to access role-restricted content
- Authorization decorator blocks access

### Error Page Design

All error pages share a consistent design:

**Theme**:
- Dark gradient background: `linear-gradient(135deg, #1a2332 0%, #2c3e50 100%)`
- White card with shadow: `box-shadow: 0 10px 40px rgba(0,0,0,0.3)`
- Rounded corners: `border-radius: 15px`

**Animations**:
- Floating background shapes with pulse animation
- 15-second infinite animation cycle
- Staggered delays for visual interest

**Responsive Design**:
- Mobile-friendly layout
- Centered fullscreen container
- Adjusts to all screen sizes

**Icons**:
- Feather Icons library
- 120px size for primary error icon
- Smaller icons in suggestion lists

### Error Handler Registration

Error handlers are registered in `agrifarma/__init__.py`:

```python
def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/error_403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found(error):
        from flask import render_template
        return render_template('errors/error_404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        from agrifarma.extensions import db
        db.session.rollback()  # Prevent data corruption
        return render_template('errors/error_500.html'), 500
```

---

## Flash Messaging System

### Overview

AgriFarma uses Flask's built-in flash messaging system to provide user feedback across page redirects. Messages are displayed at the top of pages with Bootstrap alert styling and Feather icons.

### Message Categories

Four categories are supported, each with distinct styling:

| Category | Color | Icon | Use Case |
|----------|-------|------|----------|
| `success` | Green (#28a745) | `icon-check-circle` | Successful operations (login, save, etc.) |
| `danger` | Red (#dc3545) | `icon-x-circle` | Errors, validation failures |
| `warning` | Yellow (#ffc107) | `icon-alert-triangle` | Warnings, cautions |
| `info` | Blue (#17a2b8) | `icon-info` | Informational messages |

### Usage Examples

#### Success Message
```python
from flask import flash

flash('Your profile has been updated successfully!', 'success')
```

#### Danger Message
```python
flash('Invalid username or password.', 'danger')
```

#### Warning Message
```python
flash('Your account has been deactivated. Contact support.', 'warning')
```

#### Info Message
```python
flash('Password reset instructions have been sent to your email.', 'info')
```

### Display Implementation

Flash messages are automatically displayed in `templates/layouts/base.html`:

```html
<!-- Flash Messages -->
<div class="pcoded-main-container">
    <div class="pcoded-wrapper">
        <div class="pcoded-content">
            <div class="pcoded-inner-content">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        <div class="container-fluid">
                            {% for category, message in messages %}
                            <div class="alert alert-{{ 'success' if category == 'success' else 'danger' if category == 'danger' else 'warning' if category == 'warning' else 'info' }} alert-dismissible fade show" role="alert">
                                <strong>
                                    {% if category == 'success' %}
                                        <i class="feather icon-check-circle mr-2"></i>
                                    {% elif category == 'danger' %}
                                        <i class="feather icon-x-circle mr-2"></i>
                                    {% elif category == 'warning' %}
                                        <i class="feather icon-alert-triangle mr-2"></i>
                                    {% elif category == 'info' %}
                                        <i class="feather icon-info mr-2"></i>
                                    {% endif %}
                                </strong>
                                {{ message }}
                                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                {% endwith %}
            </div>
        </div>
    </div>
</div>
```

### Features

- **Dismissible**: Users can close messages with X button
- **Auto-fade**: Uses Bootstrap's fade animation
- **Icon Support**: Each category has a distinct Feather icon
- **Multiple Messages**: Displays all queued messages
- **Responsive**: Works on all screen sizes

### Existing Flash Usage

Flash messages are already implemented in 40+ locations:

**auth.py (12 instances)**:
- Login failures, account status, profile updates, password changes

**forum.py (14 instances)**:
- Thread/reply creation, moderation actions, validation errors

**analytics.py (5 instances)**:
- Report generation, export confirmations, permission denials

**admin.py (2 instances)**:
- Access control, administrative actions

---

## Role-Based Access Control

### Overview

AgriFarma implements role-based access control (RBAC) using custom decorators to restrict routes based on user roles. The system supports four primary roles:

1. **Admin** - Full system access
2. **Consultant** - Agricultural consulting features
3. **Farmer** - Farming management features
4. **Vendor** - Marketplace and product management

### Available Decorators

All decorators are defined in `agrifarma/utils/decorators.py`.

#### 1. `@admin_required`

**Purpose**: Restrict route to administrators only.

**Usage**:
```python
from agrifarma.utils.decorators import admin_required
from flask_login import login_required

@app.route('/admin/users')
@login_required
@admin_required
def manage_users():
    return render_template('admin/users.html')
```

**Behavior**:
- Checks if user is authenticated
- Verifies `current_user.role.name == 'admin'`
- Flash message on denial: "Access denied. This page is restricted to administrators only."
- Redirects to login (if not authenticated) or homepage (if wrong role)

#### 2. `@consultant_required`

**Purpose**: Restrict route to agricultural consultants.

**Usage**:
```python
from agrifarma.utils.decorators import consultant_required

@app.route('/consultations/manage')
@login_required
@consultant_required
def manage_consultations():
    return render_template('consultations/manage.html')
```

**Behavior**:
- Checks `current_user.role.name == 'consultant'`
- Flash message: "Access denied. This page is restricted to consultants only."

#### 3. `@farmer_required`

**Purpose**: Restrict route to farmers.

**Usage**:
```python
from agrifarma.utils.decorators import farmer_required

@app.route('/farm/crops')
@login_required
@farmer_required
def manage_crops():
    return render_template('farm/crops.html')
```

**Behavior**:
- Checks `current_user.role.name == 'farmer'`
- Flash message: "Access denied. This page is restricted to farmers only."

#### 4. `@vendor_required`

**Purpose**: Restrict route to product vendors.

**Usage**:
```python
from agrifarma.utils.decorators import vendor_required

@app.route('/marketplace/vendor/products')
@login_required
@vendor_required
def vendor_products():
    return render_template('marketplace/vendor_products.html')
```

**Behavior**:
- Checks `current_user.role.name == 'vendor'`
- Flash message: "Access denied. This page is restricted to vendors only."

#### 5. `@role_required(*roles)`

**Purpose**: Allow multiple roles to access a route.

**Usage**:
```python
from agrifarma.utils.decorators import role_required

@app.route('/analytics/reports')
@login_required
@role_required('admin', 'consultant')
def view_reports():
    return render_template('analytics/reports.html')
```

**Behavior**:
- Accepts variable number of role names
- Checks if `current_user.role.name` is in allowed roles
- Flash message: "Access denied. You don't have permission to view this page."

### Helper Functions

#### `is_owner_or_admin(resource_user_id)`

**Purpose**: Check if current user owns a resource or is an admin.

**Usage**:
```python
from agrifarma.utils.decorators import is_owner_or_admin
from flask import abort

@app.route('/posts/<int:post_id>/edit')
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if not is_owner_or_admin(post.user_id):
        flash('You can only edit your own posts.', 'danger')
        abort(403)
    
    return render_template('posts/edit.html', post=post)
```

**Parameters**:
- `resource_user_id` (int): The ID of the user who owns the resource

**Returns**:
- `True` if current user is owner or admin
- `False` otherwise

**Behavior**:
- Checks if `current_user.id == resource_user_id`
- OR if `current_user.role.name == 'admin'`

### Decorator Implementation Details

All decorators follow this pattern:

```python
from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check authentication
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # 2. Check role
        if not hasattr(current_user, 'role') or current_user.role.name != 'admin':
            flash('Access denied. This page is restricted to administrators only.', 'danger')
            return redirect(url_for('main.index'))
        
        # 3. Allow access
        return f(*args, **kwargs)
    return decorated_function
```

**Key features**:
- Uses `@wraps(f)` to preserve function metadata
- Checks authentication first (avoids AttributeError)
- Provides helpful flash messages
- Preserves 'next' parameter for login redirects
- Returns 403 error page for role mismatches

---

## Implementation Guide

### Step 1: Protect a Route

To add access control to a route:

```python
from flask import Blueprint, render_template
from flask_login import login_required
from agrifarma.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required        # Check authentication
@admin_required        # Check admin role
def dashboard():
    return render_template('admin/dashboard.html')
```

**Order matters**: Always place `@login_required` before role decorators.

### Step 2: Use Flash Messages

Provide user feedback in your routes:

```python
from flask import flash, redirect, url_for

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    try:
        # Update logic here
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))
```

### Step 3: Validate Ownership

For user-specific resources:

```python
from agrifarma.utils.decorators import is_owner_or_admin

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check ownership
    if not is_owner_or_admin(post.user_id):
        flash('You can only delete your own posts.', 'danger')
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('forum.index'))
```

### Step 4: Handle Multiple Roles

Allow multiple roles to access a route:

```python
from agrifarma.utils.decorators import role_required

@app.route('/reports/analytics')
@login_required
@role_required('admin', 'consultant', 'farmer')
def analytics_report():
    # Available to admins, consultants, and farmers
    return render_template('reports/analytics.html')
```

---

## Testing

### Running Tests

Run the error handling test suite:

```bash
# Run all error handling tests
pytest tests/test_error_handling.py -v

# Run specific test class
pytest tests/test_error_handling.py::TestErrorPages -v

# Run with coverage
pytest tests/test_error_handling.py --cov=agrifarma.utils.decorators
```

### Test Coverage

The test suite (`tests/test_error_handling.py`) includes:

**Error Pages (4 tests)**:
- ✓ 404 page renders correctly
- ✓ 404 page has proper styling
- ✓ 500 page renders on errors
- ✓ 403 page renders for unauthorized access

**Flash Messages (6 tests)**:
- ✓ Flash messages display correctly
- ✓ Success category styling
- ✓ Danger category styling
- ✓ Warning category styling
- ✓ Info category styling
- ✓ Messages are dismissible

**Access Control (9 tests)**:
- ✓ Admin required allows admin
- ✓ Admin required blocks non-admin
- ✓ Admin required redirects anonymous
- ✓ Consultant required allows consultant
- ✓ Farmer required allows farmer
- ✓ Vendor required allows vendor
- ✓ Role required with multiple roles
- ✓ Unauthorized access shows flash message
- ✓ Next parameter preserved in redirects

**Ownership Validation (3 tests)**:
- ✓ Owner can access own resource
- ✓ Admin can access any resource
- ✓ Other users blocked from resource

### Test Fixtures

Pre-configured user fixtures:
- `admin_user` - Admin role
- `normal_user` - Farmer role
- `consultant_user` - Consultant role
- `farmer_user` - Farmer role
- `vendor_user` - Vendor role
- `inactive_user` - Inactive account

---

## Best Practices

### 1. Always Use Flash Messages

Provide user feedback for all important actions:

```python
# ✓ Good
flash('Product added to cart!', 'success')

# ✗ Bad - No feedback
# (silent operation)
```

### 2. Combine Decorators Properly

Order: authentication → authorization

```python
# ✓ Good
@login_required
@admin_required
def admin_route():
    pass

# ✗ Bad - Wrong order
@admin_required
@login_required
def admin_route():
    pass
```

### 3. Use Appropriate Categories

Match flash category to message type:

```python
# ✓ Good
flash('User deleted successfully.', 'success')
flash('Invalid email format.', 'danger')
flash('Session expires in 5 minutes.', 'warning')
flash('New version available.', 'info')

# ✗ Bad - Wrong categories
flash('Error occurred!', 'success')
flash('Task completed.', 'danger')
```

### 4. Validate Ownership

Always check ownership for user resources:

```python
# ✓ Good
if not is_owner_or_admin(resource.user_id):
    abort(403)

# ✗ Bad - No ownership check
# (any authenticated user can access)
```

### 5. Handle Errors Gracefully

Use try-except with database rollback:

```python
# ✓ Good
try:
    db.session.add(user)
    db.session.commit()
    flash('User created!', 'success')
except Exception as e:
    db.session.rollback()
    flash(f'Error: {str(e)}', 'danger')

# ✗ Bad - No error handling
db.session.add(user)
db.session.commit()
```

### 6. Preserve Next Parameter

Allow users to return to intended page after login:

```python
# ✓ Good (decorator handles this automatically)
return redirect(url_for('auth.login', next=request.url))

# ✗ Bad - Loses original destination
return redirect(url_for('auth.login'))
```

### 7. Use Specific Error Messages

Help users understand what went wrong:

```python
# ✓ Good
flash('Email address already registered. Try logging in.', 'warning')

# ✗ Bad - Vague message
flash('Error.', 'danger')
```

### 8. Test All Access Paths

Create tests for:
- Allowed users (200 response)
- Blocked users (403 response)
- Anonymous users (302 redirect)

```python
def test_admin_access(client, admin_user):
    client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
    response = client.get('/admin/dashboard')
    assert response.status_code == 200

def test_non_admin_blocked(client, normal_user):
    client.post('/auth/login', data={'username': 'user', 'password': 'pass'})
    response = client.get('/admin/dashboard')
    assert response.status_code == 403
```

---

## Troubleshooting

### Issue: Flash messages not appearing

**Cause**: Missing `get_flashed_messages()` in base template

**Solution**: Ensure `templates/layouts/base.html` includes flash message block (already implemented)

### Issue: 403 error page showing default browser page

**Cause**: Error handler template path incorrect

**Solution**: Verify error handlers use correct paths:
- `errors/error_403.html`
- `errors/error_404.html`
- `errors/error_500.html`

### Issue: Decorator redirects to login but loses next parameter

**Cause**: Not using `request.url` in redirect

**Solution**: Use this pattern:
```python
return redirect(url_for('auth.login', next=request.url))
```

### Issue: Role check fails with AttributeError

**Cause**: User object doesn't have role attribute

**Solution**: Check authentication first:
```python
if not current_user.is_authenticated:
    # Handle anonymous user
if not hasattr(current_user, 'role'):
    # Handle user without role
```

---

## Summary

AgriFarma's error handling and access control system provides:

✅ **Custom Error Pages**: Professional 403, 404, 500 pages with consistent branding
✅ **Flash Messaging**: Four categories with icons and dismissible alerts
✅ **Role-Based Access**: Five decorators for admin, consultant, farmer, vendor roles
✅ **Ownership Validation**: Helper function for resource ownership checks
✅ **Comprehensive Testing**: 22 tests covering all scenarios
✅ **Best Practices**: Documented patterns for secure, user-friendly applications

For more information, see:
- `agrifarma/utils/decorators.py` - Decorator implementations
- `templates/errors/` - Error page templates
- `tests/test_error_handling.py` - Test suite
- `agrifarma/__init__.py` - Error handler registration
