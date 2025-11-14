"""
Main routes for the application.
Handles homepage and general pages.
"""
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from agrifarma.extensions import db
from sqlalchemy import text

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Homepage route - redirects to dashboard."""
    from flask import redirect, url_for
    return redirect(url_for('main.dashboard'))

@main_bp.route('/shop')
def shop_redirect():
    """Convenience route mapping /shop to marketplace listing."""
    from flask import redirect, url_for
    return redirect(url_for('marketplace.index'))


@main_bp.route('/health')
def health():
    """Lightweight health/status endpoint.

    Returns JSON with app status and a simple database connectivity check.
    Safe for uptime probes. Avoids heavy queries.
    """
    from flask import jsonify
    status = 'ok'
    db_ok = True
    try:
        # Minimal DB ping (SQLite: simple select 1)
        db.session.execute(text('SELECT 1'))
    except Exception as exc:
        db_ok = False
        status = 'degraded'
    return jsonify({
        'status': status,
        'database': 'ok' if db_ok else 'error',
        'version': '1.0',
        'service': 'agrifarma'
    }), (200 if db_ok else 500)


@main_bp.route('/about')
def about():
    """About page route with its own background."""
    page_bg = '/static/images/Backgrounds/pexels-quang-nguyen-vinh-222549-2135677.jpg'
    return render_template('home/about.html', title='About Us', segment='about', page_bg=page_bg)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with form submission support."""
    from flask import request, flash
    
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you can add email sending logic or save to database
        # For now, just show a success message
        flash(f'Thank you {name}! Your message has been received. We will contact you soon.', 'success')
        
    return render_template('home/contact.html', title='Contact Us', segment='contact')


@main_bp.route('/faqs')
def faqs():
    """FAQs page route with frequently asked questions."""
    return render_template('home/faqs.html', title='FAQs', segment='faqs')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route with role-based data and quick stats."""
    from agrifarma.models.forum import Thread
    from agrifarma.models.product import Product
    from agrifarma.models.consultancy import ConsultantProfile
    from agrifarma.models.blog import BlogPost
    from agrifarma.models.user import User
    
    # Get quick statistics for dashboard cards
    total_threads = Thread.query.filter_by(is_deleted=False).count()
    total_products = Product.query.filter_by(is_active=True).count()
    total_consultants = ConsultantProfile.query.filter_by(is_verified=True).count()
    total_blogs = BlogPost.query.filter_by(is_published=True, is_deleted=False).count()
    
    # Get latest forum posts
    latest_threads = Thread.query.filter_by(is_deleted=False).order_by(
        Thread.last_activity.desc()
    ).limit(5).all()
    
    # Get recommended consultants (top rated)
    recommended_consultants = ConsultantProfile.query.filter_by(
        is_verified=True
    ).order_by(ConsultantProfile.rating.desc()).limit(3).all()
    
    # Get featured products
    featured_products = Product.query.filter_by(
        is_active=True,
        is_featured=True
    ).order_by(Product.sold_count.desc()).limit(4).all()
    
    # Get recent blogs
    recent_blogs = BlogPost.query.filter_by(
        is_published=True,
        is_deleted=False
    ).order_by(BlogPost.published_at.desc()).limit(3).all()
    
    # Role-specific data
    role_name = current_user.role.name if current_user.role else 'guest'
    
    # Farmer-specific: their products
    my_products = []
    if role_name == 'farmer':
        my_products = Product.query.filter_by(
            vendor_id=current_user.id,
            is_active=True
        ).limit(5).all()
    
    # Admin-specific: platform stats
    admin_stats = {}
    if role_name == 'admin':
        admin_stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_threads': total_threads,
            'total_products': total_products,
            'total_consultants': total_consultants,
            'total_blogs': total_blogs
        }
    
    return render_template('dashboard.html',
                         title='Dashboard',
                         segment='dashboard',
                         total_threads=total_threads,
                         total_products=total_products,
                         total_consultants=total_consultants,
                         total_blogs=total_blogs,
                         latest_threads=latest_threads,
                         recommended_consultants=recommended_consultants,
                         featured_products=featured_products,
                         recent_blogs=recent_blogs,
                         my_products=my_products,
                         admin_stats=admin_stats)


# UI Components Routes (for sidebar navigation)
# Note: /profile route is handled by auth.py
@main_bp.route('/profile.html')
@login_required
def profile_page():
    """Profile page route - redirects to auth profile."""
    from flask import redirect, url_for
    return redirect(url_for('auth.profile'))


@main_bp.route('/bc_tabs.html')
@main_bp.route('/bc_tabs')
def tabs_page():
    """Tabs component page."""
    return render_template('home/bc_tabs.html', title='Tabs', segment='bc_tabs')


@main_bp.route('/chart-morris.html')
@main_bp.route('/chart-morris')
def chart_morris():
    """Morris charts page."""
    return render_template('home/chart-morris.html', title='Charts', segment='chart-morris')


@main_bp.route('/bc_badges.html')
@main_bp.route('/bc_badges')
def badges_page():
    """Badges component page."""
    return render_template('home/bc_badges.html', title='Badges', segment='bc_badges')


@main_bp.route('/bc_breadcrumb-pagination.html')
@main_bp.route('/bc_breadcrumb-pagination')
def breadcrumb_page():
    """Breadcrumb component page."""
    return render_template('home/bc_breadcrumb-pagination.html', title='Breadcrumb', segment='bc_breadcrumb')


@main_bp.route('/bc_button.html')
@main_bp.route('/bc_button')
def button_page():
    """Button component page."""
    return render_template('home/bc_button.html', title='Buttons', segment='bc_button')


@main_bp.route('/bc_collapse.html')
@main_bp.route('/bc_collapse')
def collapse_page():
    """Collapse component page."""
    return render_template('home/bc_collapse.html', title='Collapse', segment='bc_collapse')


@main_bp.route('/bc_typography.html')
@main_bp.route('/bc_typography')
def typography_page():
    """Typography component page."""
    return render_template('home/bc_typography.html', title='Typography', segment='bc_typography')


@main_bp.route('/form_elements.html')
@main_bp.route('/form_elements')
def form_elements():
    """Form elements page."""
    return render_template('home/form_elements.html', title='Form Elements', segment='form_elements')


@main_bp.route('/icon-feather.html')
@main_bp.route('/icon-feather')
def icon_feather():
    """Feather icons page."""
    return render_template('home/icon-feather.html', title='Icons', segment='icon-feather')


@main_bp.route('/map-google.html')
@main_bp.route('/map-google')
def map_google():
    """Google maps page."""
    return render_template('home/map-google.html', title='Maps', segment='map-google')


@main_bp.route('/tbl_bootstrap.html')
@main_bp.route('/tbl_bootstrap')
def table_bootstrap():
    """Bootstrap tables page."""
    return render_template('home/tbl_bootstrap.html', title='Tables', segment='tbl_bootstrap')
