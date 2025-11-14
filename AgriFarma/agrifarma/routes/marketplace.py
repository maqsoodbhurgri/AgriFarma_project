"""
Marketplace routes for e-commerce functionality.
Implements: product listing, product detail, cart, checkout, orders.
Cart is session-based; checkout creates Order and OrderItems.
"""
from datetime import datetime
import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_required, current_user

from agrifarma.extensions import db
from agrifarma.models.product import Product, Order, OrderItem
from agrifarma.models.cart import CartItem
from agrifarma.models.product_review import ProductReview
from agrifarma.forms.marketplace import CheckoutForm
from agrifarma.forms.product import ProductForm, ReviewForm
from agrifarma.utils.decorators import vendor_required, admin_required

marketplace_bp = Blueprint('marketplace', __name__)


def _get_cart():
    """Return the cart dict from session, ensuring structure."""
    cart = session.get('cart') or {}
    # Normalize keys to str to avoid JSON issues
    session['cart'] = {str(k): int(v) for k, v in cart.items()}
    session.modified = True
    return session['cart']


def _cart_totals():
    """Compute cart totals and items list with product snapshots."""
    cart = _get_cart()
    items = []
    subtotal = 0.0
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue
        product = Product.query.filter_by(id=pid, is_active=True).first()
        if not product:
            continue
        unit_price = product.price
        total_price = round(unit_price * qty, 2)
        subtotal = round(subtotal + total_price, 2)
        items.append({
            'product': product,
            'quantity': qty,
            'unit_price': unit_price,
            'total_price': total_price,
        })
    tax_amount = round(subtotal * 0.0, 2)
    shipping_fee = 0.0
    total = round(subtotal + tax_amount + shipping_fee, 2)
    return items, subtotal, tax_amount, shipping_fee, total


def _generate_order_number():
    return 'AF-' + datetime.utcnow().strftime('%Y%m%d') + '-' + ''.join(random.choices(string.digits, k=6))


@marketplace_bp.route('/')
def index():
    """Marketplace product listing with simple filters and featured section."""
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', '').strip()  # price_asc, price_desc, popularity, rating, newest
    try:
        min_price = float(request.args.get('min_price', '').strip()) if request.args.get('min_price') else None
    except ValueError:
        min_price = None
    try:
        max_price = float(request.args.get('max_price', '').strip()) if request.args.get('max_price') else None
    except ValueError:
        max_price = None
    show_summary = request.args.get('summary') == '1'

    query = Product.query.filter_by(is_active=True)
    if q:
        like = f"%{q}%"
        query = query.filter(Product.name.ilike(like) | Product.description.ilike(like) | Product.brand.ilike(like))
    if category:
        query = query.filter_by(category=category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Sorting mapping
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popularity':  # sold_count desc
        query = query.order_by(Product.sold_count.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:  # newest default
        query = query.order_by(Product.created_at.desc())

    featured_products = query.filter(Product.is_featured == True).limit(8).all()
    products = query.all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    price_summary = []
    if show_summary:
        # Inline pandas summary: avg price & total sold per category (active products only)
        from sqlalchemy import func
        summary_rows = db.session.query(
            Product.category.label('category'),
            func.count(Product.id).label('product_count'),
            func.avg(Product.price).label('avg_price'),
            func.sum(Product.sold_count).label('total_sold')
        ).filter(Product.is_active == True).group_by(Product.category).all()
        try:
            import pandas as pd
            df = pd.DataFrame([
                {
                    'category': r.category or 'Uncategorized',
                    'product_count': int(r.product_count or 0),
                    'avg_price': float(r.avg_price or 0),
                    'total_sold': int(r.total_sold or 0)
                } for r in summary_rows
            ])
            # Sort by total_sold descending for display
            df = df.sort_values('total_sold', ascending=False)
            price_summary = df.to_dict(orient='records')
        except Exception:
            # Fallback without pandas if error occurs
            price_summary = [
                {
                    'category': r.category or 'Uncategorized',
                    'product_count': int(r.product_count or 0),
                    'avg_price': float(r.avg_price or 0),
                    'total_sold': int(r.total_sold or 0)
                } for r in summary_rows
            ]

    return render_template('marketplace.html', title='Marketplace', products=products, featured_products=featured_products, categories=categories,
                           q=q, selected_category=category, sort=sort, min_price=min_price, max_price=max_price,
                           show_summary=show_summary, price_summary=price_summary)


@marketplace_bp.route('/product/<int:product_id>')
def product(product_id):
    """Product detail page."""
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    # Increment views
    product.increment_views()
    # Related products from same category
    related_products = Product.query.filter(Product.category == product.category, Product.id != product.id, Product.is_active == True).limit(4).all()
    review_form = ReviewForm()
    reviews = ProductReview.query.filter_by(product_id=product.id).order_by(ProductReview.created_at.desc()).limit(20).all()
    return render_template('marketplace_item.html', title=product.name, product=product, related_products=related_products, review_form=review_form, reviews=reviews)


@marketplace_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def product_review(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    form = ReviewForm()
    if form.validate_on_submit():
        # Prevent duplicate simple review per user (optional; allow multiple?)
        existing = ProductReview.query.filter_by(product_id=product.id, user_id=current_user.id).first()
        if existing:
            flash('You have already reviewed this product.', 'warning')
        else:
            rating = int(form.rating.data)
            review = ProductReview(product_id=product.id, user_id=current_user.id, rating=rating, comment=form.comment.data)
            db.session.add(review)
            # Update product aggregate
            product.review_count = (product.review_count or 0) + 1
            # Recalculate average rating
            total_ratings = (product.rating or 0) * (product.review_count - 1) + rating
            product.rating = round(total_ratings / product.review_count, 2)
            db.session.commit()
            flash('Review submitted.', 'success')
    else:
        flash('Invalid review submission.', 'danger')
    return redirect(url_for('marketplace.product', product_id=product.id))


@marketplace_bp.route('/product/new', methods=['GET', 'POST'])
@login_required
@vendor_required
def product_new():
    """Create a new product listing."""
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            # Check slug uniqueness
            existing_product = Product.query.filter_by(slug=form.slug.data).first()
            if existing_product:
                flash('A product with this slug already exists. Please choose a different slug.', 'danger')
                return render_template('marketplace/product_form.html', title='New Product', form=form, mode='new')
            
            # Auto-pick product image if not provided
            def auto_image(name: str, category: str, provided: str) -> str:
                if provided:
                    return provided
                # Mirror the mapping used in seeding for consistency
                keyword_image_map = {
                    'wheat': '/static/images/products/wheat.jpg',
                    'rice': '/static/images/products/rice.jpg',
                    'cotton': '/static/images/products/cotton.jpg',
                    'corn': '/static/images/products/corn.jpg',
                    'potato': '/static/images/products/potato.jpg',
                    'tomato': '/static/images/products/tomato.jpg',
                    'onion': '/static/images/products/onion.jpg',
                    'sugarcane': '/static/images/products/sugarcane.jpg',
                    'npk': '/static/images/products/npk.jpg',
                    'urea': '/static/images/products/urea.jpg',
                    'dap': '/static/images/products/dap.jpg',
                    'compost': '/static/images/products/compost.jpg',
                    'insecticide': '/static/images/products/insecticide.jpg',
                    'fungicide': '/static/images/products/fungicide.jpg',
                    'herbicide': '/static/images/products/herbicide.jpg',
                    'sprinkler': '/static/images/products/sprinkler.jpg',
                    'hoe': '/static/images/products/hoe.jpg',
                    'shears': '/static/images/products/shears.jpg',
                    'water pump': '/static/images/products/water-pump.jpg',
                    'tractor tire': '/static/images/products/tractor-tire.jpg',
                    'plow': '/static/images/products/plow.jpg',
                    'harvester': '/static/images/products/harvester.jpg',
                }
                key = (name or '').lower()
                for kw in sorted(keyword_image_map.keys(), key=lambda k: -len(k)):
                    if kw in key:
                        return keyword_image_map[kw]
                # category defaults
                cat = (category or '').lower()
                cat_defaults = {
                    'seeds': keyword_image_map.get('wheat'),
                    'fertilizers': keyword_image_map.get('npk'),
                    'pesticides': keyword_image_map.get('insecticide'),
                    'tools': keyword_image_map.get('sprinkler'),
                    'equipment': keyword_image_map.get('tractor tire') or keyword_image_map.get('plow'),
                }
                return cat_defaults.get(cat) or '/static/images/Backgrounds/pexels-quang-nguyen-vinh-222549-2131784.jpg'
            
            # Create new product
            p = Product(
                name=form.name.data,
                slug=form.slug.data,
                description=form.description.data,
                category=form.category.data,
                subcategory=form.subcategory.data,
                price=form.price.data,
                original_price=form.original_price.data or None,
                stock_quantity=form.stock_quantity.data,
                sku=form.sku.data,
                unit=form.unit.data,
                weight=form.weight.data or None,
                brand=form.brand.data,
                manufacturer=form.manufacturer.data,
                image_url=auto_image(form.name.data, form.category.data, form.image_url.data),
                is_active=form.is_active.data,
                is_featured=form.is_featured.data,
                vendor_id=current_user.id,
            )
            
            db.session.add(p)
            db.session.commit()
            
            flash(f'Product "{p.name}" has been successfully created!', 'success')
            return redirect(url_for('marketplace.product', product_id=p.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'danger')
            return render_template('marketplace/product_form.html', title='New Product', form=form, mode='new')
    
    # Display form validation errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return render_template('marketplace/product_form.html', title='New Product', form=form, mode='new')


@marketplace_bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    # Permissions: vendor owner or admin
    if product.vendor_id != current_user.id and not current_user.is_admin():
        abort(403)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.slug = form.slug.data
        product.description = form.description.data
        product.category = form.category.data
        product.subcategory = form.subcategory.data
        product.price = form.price.data
        product.original_price = form.original_price.data or None
        product.stock_quantity = form.stock_quantity.data
        product.sku = form.sku.data
        product.unit = form.unit.data
        product.weight = form.weight.data or None
        product.brand = form.brand.data
        product.manufacturer = form.manufacturer.data
        # If image field left empty, auto-pick based on name/category
        def auto_image(name: str, category: str, provided: str) -> str:
            if provided:
                return provided
            keyword_image_map = {
                'wheat': '/static/images/products/wheat.jpg',
                'rice': '/static/images/products/rice.jpg',
                'cotton': '/static/images/products/cotton.jpg',
                'corn': '/static/images/products/corn.jpg',
                'potato': '/static/images/products/potato.jpg',
                'tomato': '/static/images/products/tomato.jpg',
                'onion': '/static/images/products/onion.jpg',
                'sugarcane': '/static/images/products/sugarcane.jpg',
                'npk': '/static/images/products/npk.jpg',
                'urea': '/static/images/products/urea.jpg',
                'dap': '/static/images/products/dap.jpg',
                'compost': '/static/images/products/compost.jpg',
                'insecticide': '/static/images/products/insecticide.jpg',
                'fungicide': '/static/images/products/fungicide.jpg',
                'herbicide': '/static/images/products/herbicide.jpg',
                'sprinkler': '/static/images/products/sprinkler.jpg',
                'hoe': '/static/images/products/hoe.jpg',
                'shears': '/static/images/products/shears.jpg',
                'water pump': '/static/images/products/water-pump.jpg',
                'tractor tire': '/static/images/products/tractor-tire.jpg',
                'plow': '/static/images/products/plow.jpg',
                'harvester': '/static/images/products/harvester.jpg',
            }
            key = (name or '').lower()
            for kw in sorted(keyword_image_map.keys(), key=lambda k: -len(k)):
                if kw in key:
                    return keyword_image_map[kw]
            cat = (category or '').lower()
            cat_defaults = {
                'seeds': keyword_image_map.get('wheat'),
                'fertilizers': keyword_image_map.get('npk'),
                'pesticides': keyword_image_map.get('insecticide'),
                'tools': keyword_image_map.get('sprinkler'),
                'equipment': keyword_image_map.get('tractor tire') or keyword_image_map.get('plow'),
            }
            return cat_defaults.get(cat) or '/static/images/Backgrounds/pexels-quang-nguyen-vinh-222549-2131784.jpg'
        product.image_url = auto_image(form.name.data, form.category.data, form.image_url.data)
        product.is_active = form.is_active.data
        product.is_featured = form.is_featured.data
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('marketplace.product', product_id=product.id))
    return render_template('marketplace/product_form.html', title='Edit Product', form=form, mode='edit', product=product)


@marketplace_bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    if product.vendor_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('marketplace.index'))


@marketplace_bp.route('/cart')
def cart_view():
    items, subtotal, tax_amount, shipping_fee, total = _cart_totals()
    return render_template('marketplace/cart.html', items=items, subtotal=subtotal, tax_amount=tax_amount, shipping_fee=shipping_fee, total=total, title='Your Cart')


@marketplace_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    qty = request.form.get('quantity', '1')
    try:
        qty = int(qty)
    except ValueError:
        qty = 1
    qty = max(1, min(qty, 100))

    if product.stock_quantity <= 0:
        flash('This product is out of stock.', 'warning')
        return redirect(url_for('marketplace.product', product_id=product.id))

    cart = _get_cart()
    current_qty = int(cart.get(str(product.id), 0))
    new_qty = min(current_qty + qty, max(1, product.stock_quantity))
    cart[str(product.id)] = new_qty
    session['cart'] = cart
    session.modified = True
    # Persist to CartItem if user is authenticated
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if existing_item:
            existing_item.set_quantity(existing_item.quantity + qty)
        else:
            ci = CartItem(user_id=current_user.id, product_id=product.id, quantity=qty)
            from agrifarma.extensions import db
            db.session.add(ci)
            db.session.commit()
    flash(f'Added {product.name} (x{qty}) to your cart.', 'success')
    return redirect(request.referrer or url_for('marketplace.cart_view'))


@marketplace_bp.route('/cart/update', methods=['POST'])
def cart_update():
    cart = _get_cart()
    updates = request.form
    for key, value in updates.items():
        if not key.startswith('qty_'):
            continue
        pid = key.replace('qty_', '')
        try:
            qty = int(value)
        except ValueError:
            qty = 1
        qty = max(0, min(qty, 100))
        if qty == 0:
            cart.pop(pid, None)
        else:
            product = Product.query.get(int(pid))
            if not product:
                continue
            qty = min(qty, max(1, product.stock_quantity))
            cart[pid] = qty
    session['cart'] = cart
    session.modified = True
    # Sync persistent cart for authenticated users
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        from agrifarma.extensions import db
        for pid_str, qty in cart.items():
            pid = int(pid_str)
            ci = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
            if ci:
                ci.set_quantity(qty)
            else:
                if qty > 0:
                    db.session.add(CartItem(user_id=current_user.id, product_id=pid, quantity=qty))
        db.session.commit()
    flash('Cart updated.', 'success')
    return redirect(url_for('marketplace.cart_view'))


@marketplace_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session['cart'] = cart
    session.modified = True
    # Remove persistent cart item
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        ci = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if ci:
            from agrifarma.extensions import db
            db.session.delete(ci)
            db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('marketplace.cart_view'))

# Alias /shop -> marketplace index for easier access
@marketplace_bp.route('/shop')
def shop_alias():
    return redirect(url_for('marketplace.index'))



@marketplace_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items, subtotal, tax_amount, shipping_fee, total = _cart_totals()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('marketplace.index'))

    form = CheckoutForm()
    if request.method == 'GET':
        # Pre-fill from profile if available
        form.full_name.data = current_user.name or current_user.username
        form.phone.data = current_user.phone or current_user.mobile or ''
        form.city.data = current_user.city or ''
        form.state.data = current_user.state or ''
    if form.validate_on_submit():
        # Create order
        order = Order(
            order_number=_generate_order_number(),
            customer_id=current_user.id,
            total_amount=total,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_fee=shipping_fee,
            discount_amount=0.0,
            status='pending',
            payment_status='unpaid',
            payment_method=form.payment_method.data,
            shipping_name=form.full_name.data,
            shipping_address=form.address.data,
            shipping_city=form.city.data,
            shipping_state=form.state.data,
            shipping_postal_code=form.postal_code.data,
            shipping_phone=form.phone.data,
            customer_notes=form.notes.data,
            order_date=datetime.utcnow(),
        )
        db.session.add(order)
        # Create order items and reduce stock
        for item in items:
            p = item['product']
            qty = item['quantity']
            unit_price = item['unit_price']
            order_item = OrderItem(
                order=order,
                product_id=p.id,
                product_name=p.name,
                product_sku=p.sku,
                quantity=qty,
                unit_price=unit_price,
                total_price=round(unit_price * qty, 2),
            )
            db.session.add(order_item)
            # Reduce stock
            p.stock_quantity = max(0, p.stock_quantity - qty)
            p.sold_count = (p.sold_count or 0) + qty
            p.in_stock = p.stock_quantity > 0
        db.session.commit()

        # Clear cart
        session['cart'] = {}
        session.modified = True

        flash('Order placed successfully! We\'ll contact you soon.', 'success')
        return redirect(url_for('marketplace.order_detail', order_id=order.id))

    return render_template('marketplace/checkout.html', form=form, items=items, subtotal=subtotal, tax_amount=tax_amount, shipping_fee=shipping_fee, total=total, title='Checkout')


@marketplace_bp.route('/orders')
@login_required
def orders():
    """Customer's purchase history."""
    user_orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('marketplace/orders.html', orders=user_orders, title='My Orders')


@marketplace_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """View specific order details."""
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()
    return render_template('marketplace/order_detail.html', order=order, title=f'Order {order.order_number}')


@marketplace_bp.route('/my-products')
@login_required
@vendor_required
def my_products():
    """Seller's product listings and sales."""
    # Get all products by current user
    products = Product.query.filter_by(vendor_id=current_user.id).order_by(Product.created_at.desc()).all()
    
    # Get orders containing seller's products
    sold_orders = db.session.query(Order).join(OrderItem).join(Product).filter(
        Product.vendor_id == current_user.id
    ).order_by(Order.order_date.desc()).limit(20).all()
    
    # Calculate stats
    total_products = len(products)
    active_products = sum(1 for p in products if p.is_active)
    total_revenue = sum(
        item.unit_price * item.quantity 
        for order in sold_orders 
        for item in order.items 
        if item.product.vendor_id == current_user.id
    )
    
    return render_template('marketplace/my_products.html', 
                         products=products,
                         sold_orders=sold_orders,
                         total_products=total_products,
                         active_products=active_products,
                         total_revenue=total_revenue,
                         title='My Products')


@marketplace_bp.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    """Admin view of all orders."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    orders_query = Order.query.order_by(Order.order_date.desc())
    
    # Filter by status if provided
    status = request.args.get('status')
    if status:
        orders_query = orders_query.filter_by(status=status)
    
    orders_pagination = orders_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate stats
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    return render_template('marketplace/admin_orders.html',
                         orders=orders_pagination.items,
                         pagination=orders_pagination,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         total_revenue=total_revenue,
                         title='Manage Orders')
