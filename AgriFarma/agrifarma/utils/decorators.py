"""
Role-based access control decorators for AgriFarma.
Provides decorators to restrict route access based on user roles.
"""
from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin role for route access.
    
    Usage:
        @app.route('/admin/users')
        @login_required
        @admin_required
        def manage_users():
            return render_template('admin/users.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if user has admin role
        if not hasattr(current_user, 'role') or current_user.role.name != 'admin':
            flash('Access denied. This page is restricted to administrators only.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def consultant_required(f):
    """
    Decorator to require consultant role for route access.
    
    Usage:
        @app.route('/consultancy/dashboard')
        @login_required
        @consultant_required
        def consultant_dashboard():
            return render_template('consultancy/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if user has consultant role
        if not hasattr(current_user, 'role') or current_user.role.name != 'consultant':
            flash('Access denied. This page is restricted to consultants only.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def farmer_required(f):
    """
    Decorator to require farmer role for route access.
    
    Usage:
        @app.route('/farm/my-crops')
        @login_required
        @farmer_required
        def my_crops():
            return render_template('farm/crops.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if user has farmer role
        if not hasattr(current_user, 'role') or current_user.role.name != 'farmer':
            flash('Access denied. This page is restricted to farmers only.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def vendor_required(f):
    """
    Decorator to require vendor or farmer role for route access.
    
    Usage:
        @app.route('/marketplace/my-products')
        @login_required
        @vendor_required
        def my_products():
            return render_template('marketplace/my_products.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if user has vendor or farmer role
        if not hasattr(current_user, 'role') or current_user.role.name not in ['vendor', 'farmer']:
            flash('Access denied. This page is restricted to farmers and vendors only.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorator to require one of multiple roles for route access.
    
    Args:
        *roles: Variable number of role names (e.g., 'admin', 'consultant')
    
    Usage:
        @app.route('/premium/content')
        @login_required
        @role_required('admin', 'consultant', 'vendor')
        def premium_content():
            return render_template('premium/content.html')
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            # Check if user has any of the required roles
            if not hasattr(current_user, 'role') or current_user.role.name not in roles:
                flash(f'Access denied. This page is restricted to {", ".join(roles)}.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


def is_owner_or_admin(resource_user_id):
    """
    Helper function to check if current user is owner of resource or admin.
    
    Args:
        resource_user_id: User ID of the resource owner
    
    Returns:
        bool: True if user is owner or admin, False otherwise
    
    Usage:
        @app.route('/product/<int:product_id>/edit')
        @login_required
        def edit_product(product_id):
            product = Product.query.get_or_404(product_id)
            if not is_owner_or_admin(product.vendor_id):
                flash('You can only edit your own products.', 'danger')
                return redirect(url_for('marketplace.index'))
            return render_template('marketplace/edit_product.html', product=product)
    """
    if not current_user.is_authenticated:
        return False
    
    # User is owner
    if current_user.id == resource_user_id:
        return True
    
    # User is admin
    if hasattr(current_user, 'role') and current_user.role.name == 'admin':
        return True
    
    return False
