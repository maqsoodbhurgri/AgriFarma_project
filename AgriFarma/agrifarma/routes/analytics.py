"""
Analytics and Reports module for admin dashboard.
Provides data insights, visual analytics, and export capabilities.
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func, extract
import pandas as pd
import json
from io import StringIO

from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.product import Product, Order, OrderItem

analytics_bp = Blueprint('analytics', __name__)


def admin_required(f):
    """Decorator to require admin role for route access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if user has admin role
        if not hasattr(current_user, 'role') or current_user.role.name != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


@analytics_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard with visual analytics using Chart.js.
    Displays: monthly sales, product categories, user registrations.
    """
    # Get date range for charts (last 12 months)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    # === MONTHLY SALES DATA (Bar Chart) ===
    monthly_sales = db.session.query(
        extract('year', Order.order_date).label('year'),
        extract('month', Order.order_date).label('month'),
        func.sum(Order.total_amount).label('revenue'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.order_date >= start_date,
        Order.status != 'cancelled'
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Format for Chart.js
    sales_labels = []
    sales_revenue = []
    sales_orders = []
    
    for sale in monthly_sales:
        month_name = datetime(int(sale.year), int(sale.month), 1).strftime('%b %Y')
        sales_labels.append(month_name)
        sales_revenue.append(float(sale.revenue or 0))
        sales_orders.append(int(sale.order_count or 0))
    
    # === PRODUCT CATEGORY DISTRIBUTION (Pie Chart) ===
    category_data = db.session.query(
        Product.category,
        func.count(Product.id).label('product_count'),
        func.sum(Product.sold_count).label('total_sold')
    ).filter(
        Product.is_active == True
    ).group_by(Product.category).all()
    
    category_labels = [cat.category for cat in category_data]
    category_counts = [int(cat.product_count) for cat in category_data]
    category_sales = [int(cat.total_sold or 0) for cat in category_data]
    
    # === USER REGISTRATIONS OVER TIME (Line Chart) ===
    user_registrations = db.session.query(
        func.date(User.join_date).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.join_date >= start_date
    ).group_by('date').order_by('date').all()
    
    registration_labels = []
    registration_counts = []
    
    for reg in user_registrations:
        registration_labels.append(reg.date.strftime('%Y-%m-%d'))
        registration_counts.append(int(reg.count))
    
    # === KEY METRICS SUMMARY ===
    # Total revenue (all time)
    total_revenue = db.session.query(
        func.sum(Order.total_amount)
    ).filter(Order.status != 'cancelled').scalar() or 0
    
    # Total orders
    total_orders = Order.query.filter(Order.status != 'cancelled').count()
    
    # Total users
    total_users = User.query.count()
    
    # Active products
    active_products = Product.query.filter_by(is_active=True).count()
    
    # Low stock products
    low_stock_count = Product.query.filter(
        Product.stock_quantity <= Product.low_stock_threshold,
        Product.is_active == True
    ).count()
    
    # Recent orders (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_orders = Order.query.filter(
        Order.order_date >= thirty_days_ago,
        Order.status != 'cancelled'
    ).count()
    
    # New users (last 30 days)
    new_users = User.query.filter(User.join_date >= thirty_days_ago).count()
    
    # Top selling product
    top_product = db.session.query(Product).order_by(Product.sold_count.desc()).first()
    
    return render_template('analytics/admin_dashboard.html',
                         title='Admin Dashboard',
                         # Chart data
                         sales_labels=json.dumps(sales_labels),
                         sales_revenue=json.dumps(sales_revenue),
                         sales_orders=json.dumps(sales_orders),
                         category_labels=json.dumps(category_labels),
                         category_counts=json.dumps(category_counts),
                         category_sales=json.dumps(category_sales),
                         registration_labels=json.dumps(registration_labels),
                         registration_counts=json.dumps(registration_counts),
                         # Summary metrics
                         total_revenue=total_revenue,
                         total_orders=total_orders,
                         total_users=total_users,
                         active_products=active_products,
                         low_stock_count=low_stock_count,
                         recent_orders=recent_orders,
                         new_users=new_users,
                         top_product=top_product)


@analytics_bp.route('/admin/reports')
@login_required
@admin_required
def reports():
    """
    Admin reports page with filterable tabular data and export options.
    Supports CSV and JSON export.
    """
    # Get filter parameters
    report_type = request.args.get('report_type', 'top_products')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    export_format = request.args.get('export')
    
    # Parse dates
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.utcnow()
    
    # Generate report based on type
    report_data = None
    columns = []
    
    if report_type == 'top_products':
        # Top-selling products by date range
        query = db.session.query(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            Product.stock_quantity,
            Product.sold_count,
            (Product.sold_count * Product.price).label('revenue')
        ).filter(
            Product.created_at.between(start_date, end_date)
        )
        
        if category:
            query = query.filter(Product.category == category)
        
        products = query.order_by(Product.sold_count.desc()).limit(100).all()
        
        columns = ['ID', 'Product Name', 'Category', 'Price (PKR)', 'Stock', 'Units Sold', 'Revenue (PKR)']
        report_data = [{
            'ID': p.id,
            'Product Name': p.name,
            'Category': p.category,
            'Price (PKR)': f'{p.price:.2f}',
            'Stock': p.stock_quantity,
            'Units Sold': p.sold_count,
            'Revenue (PKR)': f'{float(p.revenue):.2f}' if p.revenue else '0.00'
        } for p in products]
    
    elif report_type == 'low_inventory':
        # Low inventory alerts
        products = Product.query.filter(
            Product.stock_quantity <= Product.low_stock_threshold,
            Product.is_active == True
        ).order_by(Product.stock_quantity.asc()).all()
        
        columns = ['ID', 'Product Name', 'Category', 'Current Stock', 'Threshold', 'Status']
        report_data = [{
            'ID': p.id,
            'Product Name': p.name,
            'Category': p.category,
            'Current Stock': p.stock_quantity,
            'Threshold': p.low_stock_threshold,
            'Status': 'Out of Stock' if p.stock_quantity == 0 else 'Low Stock'
        } for p in products]
    
    elif report_type == 'user_registrations':
        # New user registrations by date
        users = User.query.filter(
            User.join_date.between(start_date, end_date)
        ).order_by(User.join_date.desc()).all()
        
        columns = ['ID', 'Username', 'Email', 'Role', 'City', 'Profession', 'Join Date']
        report_data = [{
            'ID': u.id,
            'Username': u.username,
            'Email': u.email,
            'Role': u.role.name if u.role else 'N/A',
            'City': u.city or 'N/A',
            'Profession': u.profession or 'N/A',
            'Join Date': u.join_date.strftime('%Y-%m-%d %H:%M')
        } for u in users]
    
    elif report_type == 'orders_revenue':
        # Total orders and revenue by month
        monthly_data = db.session.query(
            extract('year', Order.order_date).label('year'),
            extract('month', Order.order_date).label('month'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            Order.order_date.between(start_date, end_date),
            Order.status != 'cancelled'
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        columns = ['Month', 'Total Orders', 'Revenue (PKR)', 'Avg Order Value (PKR)']
        report_data = [{
            'Month': datetime(int(m.year), int(m.month), 1).strftime('%B %Y'),
            'Total Orders': int(m.order_count),
            'Revenue (PKR)': f'{float(m.revenue or 0):.2f}',
            'Avg Order Value (PKR)': f'{float(m.avg_order_value or 0):.2f}'
        } for m in monthly_data]
    
    elif report_type == 'category_distribution':
        # Product category distribution
        categories = db.session.query(
            Product.category,
            func.count(Product.id).label('product_count'),
            func.sum(Product.stock_quantity).label('total_stock'),
            func.sum(Product.sold_count).label('total_sold'),
            func.avg(Product.price).label('avg_price')
        ).filter(
            Product.is_active == True
        ).group_by(Product.category).all()
        
        columns = ['Category', 'Product Count', 'Total Stock', 'Total Sold', 'Avg Price (PKR)']
        report_data = [{
            'Category': c.category,
            'Product Count': int(c.product_count),
            'Total Stock': int(c.total_stock or 0),
            'Total Sold': int(c.total_sold or 0),
            'Avg Price (PKR)': f'{float(c.avg_price or 0):.2f}'
        } for c in categories]
    
    # Handle export requests
    if export_format and report_data:
        return export_report(report_data, columns, report_type, export_format)
    
    # Get unique categories for filter
    all_categories = db.session.query(Product.category).distinct().all()
    categories_list = [c[0] for c in all_categories if c[0]]
    
    flash(f'Report generated successfully. {len(report_data) if report_data else 0} records found.', 'success')
    
    return render_template('analytics/admin_reports.html',
                         title='Admin Reports',
                         report_type=report_type,
                         report_data=report_data,
                         columns=columns,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'),
                         categories=categories_list,
                         selected_category=category)


def export_report(data, columns, report_name, export_format):
    """
    Export report data as CSV or JSON.
    
    Args:
        data: List of dictionaries containing report data
        columns: List of column names
        report_name: Name of the report
        export_format: 'csv' or 'json'
    
    Returns:
        Flask response with appropriate content type
    """
    if export_format == 'csv':
        # Create pandas DataFrame
        df = pd.DataFrame(data)
        
        # Convert to CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Create response
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={report_name}_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        
        flash('CSV report exported successfully.', 'success')
        return response
    
    elif export_format == 'json':
        # Convert to JSON
        json_data = json.dumps(data, indent=2)
        
        # Create response
        response = make_response(json_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename={report_name}_{datetime.utcnow().strftime("%Y%m%d")}.json'
        
        flash('JSON report exported successfully.', 'success')
        return response


@analytics_bp.route('/admin/reports/api/quick-stats')
@login_required
@admin_required
def quick_stats_api():
    """
    API endpoint for quick statistics (AJAX).
    Returns JSON with key metrics.
    """
    # Calculate quick stats
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status != 'cancelled'
    ).scalar() or 0
    
    total_orders = Order.query.filter(Order.status != 'cancelled').count()
    total_users = User.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    low_stock = Product.query.filter(
        Product.stock_quantity <= Product.low_stock_threshold
    ).count()
    
    # Last 30 days stats
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.order_date >= thirty_days_ago,
        Order.status != 'cancelled'
    ).scalar() or 0
    
    recent_orders = Order.query.filter(
        Order.order_date >= thirty_days_ago,
        Order.status != 'cancelled'
    ).count()
    
    new_users = User.query.filter(User.join_date >= thirty_days_ago).count()
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_orders': total_orders,
        'total_users': total_users,
        'active_products': active_products,
        'low_stock_products': low_stock,
        'recent_revenue': float(recent_revenue),
        'recent_orders': recent_orders,
        'new_users': new_users
    })
