"""
Admin routes for managing the application.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
import os
from agrifarma.extensions import db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard route."""
    return render_template('admin/dashboard.html', title='Admin Dashboard')


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users route with role filter."""
    from agrifarma.models.user import User
    from agrifarma.models.role import Role
    from agrifarma.extensions import db
    role_filter = request.args.get('role', '').strip()
    query = User.query
    if role_filter:
        query = query.join(Role).filter(Role.name == role_filter)
    users_list = query.order_by(User.join_date.desc()).all()
    roles = Role.query.all()
    return render_template('admin/user.html', title='Manage Users', users=users_list, roles=roles, role_filter=role_filter)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View detailed user profile and activity."""
    from agrifarma.models.user import User
    from agrifarma.models.product import Order
    from agrifarma.models.consultancy import ConsultationBooking
    user = User.query.get_or_404(user_id)
    # User orders
    orders = Order.query.filter_by(customer_id=user.id).order_by(Order.order_date.desc()).limit(10).all()
    # Total spent
    total_spent = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.customer_id == user.id, Order.status != 'cancelled'
    ).scalar() or 0
    # Consultation bookings
    bookings = ConsultationBooking.query.filter_by(user_id=user.id).order_by(ConsultationBooking.created_at.desc()).limit(5).all()
    return render_template('admin/user_detail.html', title=f'User: {user.username}', user=user, orders=orders, total_spent=total_spent, bookings=bookings)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def user_toggle_active(user_id):
    """Toggle user active status."""
    from agrifarma.models.user import User
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.username} {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user.id))


@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def user_change_role(user_id):
    """Change user role."""
    from agrifarma.models.user import User
    from agrifarma.models.role import Role
    user = User.query.get_or_404(user_id)
    new_role_id = request.form.get('role_id')
    if not new_role_id:
        flash('Role not specified.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    role = Role.query.get(int(new_role_id))
    if not role:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    user.role_id = role.id
    db.session.commit()
    flash(f'User {user.username} role changed to {role.name}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user.id))


@admin_bp.route('/consultants')
@login_required
@admin_required
def consultants():
    """Admin view of consultant profiles for verification."""
    from agrifarma.models.consultancy import ConsultantProfile
    pending = ConsultantProfile.query.filter_by(is_verified=False).all()
    verified = ConsultantProfile.query.filter_by(is_verified=True).all()
    return render_template('admin/consultants.html', title='Consultants Approval', pending=pending, verified=verified)


@admin_bp.route('/consultants/<int:profile_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_consultant(profile_id):
    from agrifarma.models.consultancy import ConsultantProfile
    profile = ConsultantProfile.query.get_or_404(profile_id)
    if profile.is_verified:
        flash('Profile already verified.', 'info')
    else:
        profile.is_verified = True
        profile.updated_at = profile.updated_at  # trigger update timestamp
        db.session.commit()
        flash('Consultant profile verified.', 'success')
    return redirect(url_for('admin.consultants'))


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings route with feature toggles."""
    from agrifarma.models.srs_compliance import SRSModule
    # Fetch or create a settings record (reusing SRSModule for simplicity; could create AppSettings model)
    checkbot_setting = SRSModule.query.filter_by(module_id='checkbot_enabled').first()
    checkbot_enabled = checkbot_setting.override_status == 'completed' if checkbot_setting else False
    return render_template('admin/settings.html', title='Settings', checkbot_enabled=checkbot_enabled)


@admin_bp.route('/settings/toggle-checkbot', methods=['POST'])
@login_required
@admin_required
def toggle_checkbot():
    """Toggle CheckBot AI feature."""
    from agrifarma.models.srs_compliance import SRSModule
    from datetime import datetime
    checkbot_setting = SRSModule.query.filter_by(module_id='checkbot_enabled').first()
    if not checkbot_setting:
        checkbot_setting = SRSModule(module_id='checkbot_enabled', name='CheckBot AI Feature')
        db.session.add(checkbot_setting)
    # Toggle status: 'completed' = enabled, 'missing' = disabled
    if checkbot_setting.override_status == 'completed':
        checkbot_setting.override_status = 'missing'
        flash('CheckBot AI disabled.', 'info')
    else:
        checkbot_setting.override_status = 'completed'
        flash('CheckBot AI enabled.', 'success')
    checkbot_setting.updated_at = datetime.utcnow()
    checkbot_setting.updated_by_id = current_user.id
    db.session.commit()
    return redirect(url_for('admin.settings'))


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Admin analytics and reports dashboard."""
    from agrifarma.models.user import User
    from agrifarma.models.product import Product, Order
    from agrifarma.models.forum import Thread, Reply
    from agrifarma.models.blog import BlogPost
    from agrifarma.models.consultancy import ConsultantProfile, ConsultationBooking
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # User statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Platform statistics
    total_threads = Thread.query.filter_by(is_deleted=False).count()
    total_replies = Reply.query.filter_by(is_deleted=False).count()
    total_products = Product.query.filter_by(is_active=True).count()
    total_blogs = BlogPost.query.filter_by(is_published=True, is_deleted=False).count()
    total_consultants = ConsultantProfile.query.filter_by(is_verified=True).count()
    
    # Sales statistics
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status != 'cancelled'
    ).scalar() or 0
    
    # Top selling products
    top_products = Product.query.filter_by(is_active=True).order_by(
        Product.sold_count.desc()
    ).limit(10).all()
    
    # Low inventory products
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= Product.low_stock_threshold,
        Product.is_active == True
    ).order_by(Product.stock_quantity).limit(10).all()
    
    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = User.query.filter(User.join_date >= thirty_days_ago).count()
    
    # Category-wise product breakdown
    category_stats = db.session.query(
        Product.category,
        func.count(Product.id).label('count'),
        func.sum(Product.sold_count).label('total_sold'),
        func.sum(Product.stock_quantity).label('total_stock')
    ).filter(Product.is_active == True).group_by(Product.category).all()
    
    return render_template('admin/reports.html',
                         title='Analytics & Reports',
                         total_users=total_users,
                         active_users=active_users,
                         new_users=new_users,
                         total_threads=total_threads,
                         total_replies=total_replies,
                         total_products=total_products,
                         total_blogs=total_blogs,
                         total_consultants=total_consultants,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         top_products=top_products,
                         low_stock_products=low_stock_products,
                         category_stats=category_stats)


# --- Orders management ---
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    """Admin orders list with optional status filter."""
    from agrifarma.models.product import Order
    status = request.args.get('status', '').strip()
    q = Order.query
    if status:
        q = q.filter_by(status=status)
    orders = q.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', title='Manage Orders', orders=orders, status=status)

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Admin product management view with basic inventory & performance metrics."""
    from agrifarma.models.product import Product, OrderItem
    from agrifarma.extensions import db
    products = Product.query.order_by(Product.created_at.desc()).all()
    total_active = Product.query.filter_by(is_active=True).count()
    low_stock = Product.query.filter(Product.stock_quantity <= Product.low_stock_threshold).count()
    featured_count = Product.query.filter_by(is_featured=True).count()
    total_sold_units = db.session.query(db.func.sum(Product.sold_count)).scalar() or 0
    # Top selling products (limit 10)
    top_selling = Product.query.filter_by(is_active=True).order_by(Product.sold_count.desc()).limit(10).all()
    # Category summary
    category_rows = db.session.query(
        Product.category, db.func.count(Product.id), db.func.sum(Product.stock_quantity), db.func.sum(Product.sold_count)
    ).group_by(Product.category).all()
    category_summary = [
        {
            'category': row[0] or 'Uncategorized',
            'product_count': int(row[1] or 0),
            'stock_total': int(row[2] or 0),
            'sold_total': int(row[3] or 0)
        } for row in category_rows if row[0]
    ]
    return render_template('admin/products.html', title='Manage Products', products=products, total_active=total_active,
                           low_stock=low_stock, featured_count=featured_count, total_sold_units=total_sold_units,
                           top_selling=top_selling, category_summary=category_summary)


@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    """Admin review management: view and moderate product reviews."""
    from agrifarma.models.product_review import ProductReview
    reviews_list = ProductReview.query.order_by(ProductReview.created_at.desc()).limit(100).all()
    return render_template('admin/reviews.html', title='Manage Reviews', reviews=reviews_list)


@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def review_delete(review_id):
    """Delete a product review."""
    from agrifarma.models.product_review import ProductReview
    review = ProductReview.query.get_or_404(review_id)
    product = review.product
    db.session.delete(review)
    # Recalculate product rating
    from agrifarma.models.product_review import ProductReview as PR
    remaining_reviews = PR.query.filter_by(product_id=product.id).all()
    if remaining_reviews:
        avg_rating = sum(r.rating for r in remaining_reviews) / len(remaining_reviews)
        product.rating = round(avg_rating, 2)
        product.review_count = len(remaining_reviews)
    else:
        product.rating = 0.0
        product.review_count = 0
    db.session.commit()
    flash('Review deleted and rating recalculated.', 'success')
    return redirect(url_for('admin.reviews'))



@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    from agrifarma.models.product import Order
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', title=f'Order {order.order_number}', order=order)


@admin_bp.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
@admin_required
def order_update(order_id):
    from agrifarma.models.product import Order
    from agrifarma.extensions import db
    order = Order.query.get_or_404(order_id)
    # Update fields
    new_status = request.form.get('status')
    payment_status = request.form.get('payment_status')
    tracking_number = request.form.get('tracking_number')
    carrier = request.form.get('carrier')

    # Validate status
    allowed_status = {'pending','processing','shipped','delivered','cancelled'}
    if new_status and new_status in allowed_status:
        order.update_status(new_status)
    if payment_status in {'unpaid','paid','refunded'}:
        order.payment_status = payment_status
        if payment_status == 'paid' and not order.paid_at:
            from datetime import datetime
            order.paid_at = datetime.utcnow()
    order.tracking_number = tracking_number or None
    order.carrier = carrier or None
    db.session.commit()
    flash('Order updated successfully.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))


# --- SRS Compliance Dashboard ---
@admin_bp.route('/srs-status')
@login_required
@admin_required
def srs_status():
    """SRS Compliance status dashboard."""
    from agrifarma.utils.srs_scanner import create_scanner
    from agrifarma.models.srs_compliance import SRSModule, SRSRequirement
    
    # Get project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Generate compliance report
    scanner = create_scanner(project_root)
    report = scanner.generate_report()
    
    # Load manual overrides from database
    overrides_modules = {m.module_id: m for m in SRSModule.query.all()}
    overrides_requirements = {r.requirement_id: r for r in SRSRequirement.query.all()}
    
    # Apply overrides to report
    for module in report['modules']:
        if module['id'] in overrides_modules:
            override = overrides_modules[module['id']]
            if override.override_status:
                module['override_status'] = override.override_status
                module['override_notes'] = override.notes
        
        for req in module['requirements']:
            if req['id'] in overrides_requirements:
                override = overrides_requirements[req['id']]
                if override.override_status:
                    req['override_status'] = override.override_status
                    req['override_notes'] = override.notes
    
    return render_template('admin/srs_compliance.html', 
                         title='SRS Compliance Status',
                         report=report)


@admin_bp.route('/srs-status/export/<format>')
@login_required
@admin_required
def srs_export(format):
    """Export SRS compliance report."""
    from agrifarma.utils.srs_scanner import create_scanner
    
    if format not in ['json', 'html']:
        flash('Invalid export format.', 'danger')
        return redirect(url_for('admin.srs_status'))
    
    # Get project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Generate and export report
    scanner = create_scanner(project_root)
    output_path = scanner.export_report(format=format)
    
    flash(f'Report exported to {output_path}', 'success')
    return redirect(url_for('admin.srs_status'))


@admin_bp.route('/srs-status/update', methods=['POST'])
@login_required
@admin_required
def srs_update():
    """Update manual override for requirement or module."""
    from agrifarma.models.srs_compliance import SRSModule, SRSRequirement
    from agrifarma.extensions import db
    from datetime import datetime
    
    item_type = request.form.get('type')  # 'module' or 'requirement'
    item_id = request.form.get('id')
    override_status = request.form.get('status')  # 'completed', 'partial', 'missing', or empty
    notes = request.form.get('notes', '')
    
    if not item_type or not item_id:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    # Validate status
    if override_status and override_status not in ['completed', 'partial', 'missing']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    if item_type == 'module':
        item = SRSModule.query.filter_by(module_id=item_id).first()
        if not item:
            # Create new record
            item = SRSModule(
                module_id=item_id,
                name=request.form.get('name', item_id)
            )
            db.session.add(item)
        
        item.override_status = override_status if override_status else None
        item.notes = notes
        item.updated_by_id = current_user.id
        item.updated_at = datetime.utcnow()
        
    elif item_type == 'requirement':
        item = SRSRequirement.query.filter_by(requirement_id=item_id).first()
        if not item:
            # Create new record
            item = SRSRequirement(
                requirement_id=item_id,
                module_id=request.form.get('module_id', ''),
                name=request.form.get('name', item_id)
            )
            db.session.add(item)
        
        item.override_status = override_status if override_status else None
        item.notes = notes
        item.updated_by_id = current_user.id
        item.updated_at = datetime.utcnow()
    else:
        return jsonify({'success': False, 'message': 'Invalid type'}), 400
    
    db.session.commit()
    flash(f'Status updated for {item_id}', 'success')
    
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True, 'message': 'Updated successfully'})
    
    return redirect(url_for('admin.srs_status'))
