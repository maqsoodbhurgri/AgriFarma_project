"""
AgriFarma - Digital Hub for Farmers in Sindh, Pakistan
Main application entry point using the app factory pattern.
"""
import os
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.role import Role
from agrifarma.models.product import Product, Order, OrderItem
from agrifarma.models.blog import BlogPost, BlogCategory, BlogComment, BlogAttachment
from agrifarma.models.consultancy import ConsultancyMessage
from agrifarma.models.srs_compliance import SRSModule, SRSRequirement

# Create the Flask application instance
app = create_app(os.getenv('FLASK_ENV') or 'development')

@app.shell_context_processor
def make_shell_context():
    """
    Create shell context for flask shell command.
    Makes db and models available in the shell.
    """
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Product': Product,
        'Order': Order,
        'OrderItem': OrderItem
    }


@app.cli.command()
def init_db():
    """Initialize the database with tables and default data."""
    db.create_all()
    
    # Create default roles if they don't exist
    roles = ['admin', 'farmer', 'consultant', 'vendor', 'academic']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    
    db.session.commit()
    print("Database initialized successfully!")


@app.cli.command()
def create_admin():
    """Create an admin user."""
    from getpass import getpass
    
    email = input("Enter admin email: ")
    username = input("Enter admin username: ")
    password = getpass("Enter admin password: ")
    password_confirm = getpass("Confirm password: ")
    
    if password != password_confirm:
        print("Passwords don't match!")
        return
    
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.flush()
    
    # Check if user already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        # Update existing user to admin
        existing_user.role_id = admin_role.id
        existing_user.is_active = True
        existing_user.is_verified = True
        existing_user.set_password(password)
        db.session.commit()
        print(f"User '{username}' has been updated to admin successfully!")
        return
    
    user = User(
        username=username,
        email=email,
        name="Administrator",
        role_id=admin_role.id,
        is_active=True,
        is_verified=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f"Admin user '{username}' created successfully!")


@app.cli.command()
def seed_data():
    """Seed database with sample products and orders for testing analytics."""
    from datetime import datetime, timedelta
    import random
    
    print("Seeding sample data...")
    
    # Get or create vendor user
    vendor_role = Role.query.filter_by(name='vendor').first()
    vendor = User.query.filter_by(role_id=vendor_role.id).first()
    
    if not vendor:
        vendor = User(
            username='vendor1',
            name='Test Vendor',
            email='vendor@agrifarma.com',
            role_id=vendor_role.id,
            is_active=True,
            profession='vendor',
            business_name='AgriFarma Supplies'
        )
        vendor.set_password('password123')
        db.session.add(vendor)
        db.session.commit()
    
    # Sample product categories and items
    categories_data = {
        'Seeds': [
            {'name': 'Wheat Seeds Premium', 'price': 1500, 'unit': 'bag'},
            {'name': 'Rice Seeds Basmati', 'price': 2000, 'unit': 'bag'},
            {'name': 'Cotton Seeds Hybrid', 'price': 1800, 'unit': 'bag'},
            {'name': 'Corn Seeds Yellow', 'price': 1200, 'unit': 'bag'},
        ],
        'Fertilizers': [
            {'name': 'NPK Fertilizer 15-15-15', 'price': 2500, 'unit': 'bag'},
            {'name': 'Urea Fertilizer', 'price': 1800, 'unit': 'bag'},
            {'name': 'DAP Fertilizer', 'price': 3000, 'unit': 'bag'},
            {'name': 'Organic Compost', 'price': 800, 'unit': 'bag'},
        ],
        'Pesticides': [
            {'name': 'Insecticide Spray', 'price': 500, 'unit': 'bottle'},
            {'name': 'Fungicide Powder', 'price': 600, 'unit': 'bottle'},
            {'name': 'Herbicide Liquid', 'price': 750, 'unit': 'bottle'},
        ],
        'Tools': [
            {'name': 'Irrigation Sprinkler', 'price': 3500, 'unit': 'piece'},
            {'name': 'Garden Hoe', 'price': 450, 'unit': 'piece'},
            {'name': 'Pruning Shears', 'price': 650, 'unit': 'piece'},
            {'name': 'Water Pump Small', 'price': 8500, 'unit': 'piece'},
        ],
        'Equipment': [
            {'name': 'Tractor Tire', 'price': 12000, 'unit': 'piece'},
            {'name': 'Plow Blade', 'price': 4500, 'unit': 'piece'},
            {'name': 'Harvester Blade', 'price': 5500, 'unit': 'piece'},
        ]
    }
    
    # Product-specific image mapper: prefer local static images under /static/images/products
    # File convention: products/<keyword>.jpg or .png. Add your own images to match keywords below.
    keyword_image_map = {
        # Seeds
        'wheat': '/static/images/products/wheat.jpg',
        'rice': '/static/images/products/rice.jpg',
        'cotton': '/static/images/products/cotton.jpg',
        'corn': '/static/images/products/corn.jpg',
        'potato': '/static/images/products/potato.jpg',
        'tomato': '/static/images/products/tomato.jpg',
        'onion': '/static/images/products/onion.jpg',
        'sugarcane': '/static/images/products/sugarcane.jpg',
        # Fertilizers
        'npk': '/static/images/products/npk.jpg',
        'urea': '/static/images/products/urea.jpg',
        'dap': '/static/images/products/dap.jpg',
        'compost': '/static/images/products/compost.jpg',
        'organic': '/static/images/products/compost.jpg',
        # Pesticides
        'insecticide': '/static/images/products/insecticide.jpg',
        'fungicide': '/static/images/products/fungicide.jpg',
        'herbicide': '/static/images/products/herbicide.jpg',
        # Tools / Equipment
        'sprinkler': '/static/images/products/sprinkler.jpg',
        'hoe': '/static/images/products/hoe.jpg',
        'shears': '/static/images/products/shears.jpg',
        'water pump': '/static/images/products/water-pump.jpg',
        'tractor tire': '/static/images/products/tractor-tire.jpg',
        'plow': '/static/images/products/plow.jpg',
        'harvester': '/static/images/products/harvester.jpg',
    }

    # Generic fallback pool (farm backgrounds) only used when no specific image is available
    image_pool = [
        '/static/images/Backgrounds/pexels-ironic-751096.jpg',
        '/static/images/Backgrounds/pexels-timmossholder-974314.jpg',
        '/static/images/Backgrounds/pexels-quang-nguyen-vinh-222549-2131784.jpg',
        '/static/images/Backgrounds/pexels-quang-nguyen-vinh-222549-2135677.jpg',
        '/static/images/Backgrounds/pexels-nc-farm-bureau-mark-2255920.jpg'
    ]
    random.shuffle(image_pool)
    pool_index = 0

    def image_for_product(name: str, category: str) -> str:
        """Pick the most specific image for a product.
        Priority: exact keyword hit in name -> category keywords -> fallback pool.
        """
        key = name.lower()
        # try multi-word keys first
        for kw in sorted(keyword_image_map.keys(), key=lambda k: -len(k)):
            if kw in key:
                return keyword_image_map[kw]
        # category-based defaults
        cat = (category or '').lower()
        category_defaults = {
            'seeds': keyword_image_map.get('wheat'),
            'fertilizers': keyword_image_map.get('npk'),
            'pesticides': keyword_image_map.get('insecticide'),
            'tools': keyword_image_map.get('sprinkler'),
            'equipment': keyword_image_map.get('tractor tire') or keyword_image_map.get('plow'),
        }
        if category_defaults.get(cat):
            return category_defaults[cat]
        # fallback rotating pool
        nonlocal pool_index
        url = image_pool[pool_index % len(image_pool)]
        pool_index += 1
        return url

    products = []
    for category, items in categories_data.items():
        for item_data in items:
            # Check if product already exists
            slug = item_data['name'].lower().replace(' ', '-')
            existing = Product.query.filter_by(slug=slug).first()
            if existing:
                continue
            
            product = Product(
                name=item_data['name'],
                slug=slug,
                description=f"High quality {item_data['name'].lower()} for agricultural use.",
                category=category,
                price=item_data['price'],
                original_price=item_data['price'] * 1.2,  # 20% discount
                stock_quantity=random.randint(50, 200),
                low_stock_threshold=10,
                unit=item_data['unit'],
                vendor_id=vendor.id,
                is_active=True,
                in_stock=True,
                sold_count=random.randint(10, 100),
                # Assign product-specific image
                image_url=image_for_product(item_data['name'], category)
            )
            db.session.add(product)
            products.append(product)
            # pool_index is incremented in fallback path when used
    
    db.session.commit()
    print(f"Created {len(products)} products.")

    # Backfill products without distinct images by assigning specific image if possible (else fallback pool)
    missing_images = Product.query.filter((Product.image_url == None) | (Product.image_url == '')).all()
    updated = 0
    for p in missing_images:
        p.image_url = image_for_product(p.name or '', p.category or '')
        updated += 1
    if updated:
        db.session.commit()
        print(f"Backfilled distinct images for {updated} existing products.")
    
    # Get or create customer users
    farmer_role = Role.query.filter_by(name='farmer').first()
    customers = User.query.filter_by(role_id=farmer_role.id).limit(5).all()
    
    if not customers:
        for i in range(5):
            customer = User(
                username=f'farmer{i+1}',
                name=f'Farmer User {i+1}',
                email=f'farmer{i+1}@agrifarma.com',
                role_id=farmer_role.id,
                is_active=True,
                profession='farmer',
                city='Karachi',
                state='Sindh'
            )
            customer.set_password('password123')
            db.session.add(customer)
            customers.append(customer)
        db.session.commit()
    
    # Create sample orders over the last 12 months
    all_products = Product.query.all()
    if not all_products:
        print("No products available to create orders.")
        return
    
    order_statuses = ['delivered', 'delivered', 'delivered', 'shipped', 'processing']
    payment_methods = ['cod', 'bank_transfer', 'card']
    
    orders_created = 0
    for month_offset in range(12):
        # Create 5-15 orders per month
        num_orders = random.randint(5, 15)
        
        for _ in range(num_orders):
            # Random date within the month
            order_date = datetime.utcnow() - timedelta(days=30*month_offset + random.randint(0, 30))
            
            customer = random.choice(customers)
            status = random.choice(order_statuses)
            
            # Create order
            order = Order(
                order_number=f'ORD-{datetime.utcnow().timestamp():.0f}-{random.randint(100, 999)}',
                customer_id=customer.id,
                status=status,
                payment_status='paid' if status in ['delivered', 'shipped'] else 'unpaid',
                payment_method=random.choice(payment_methods),
                order_date=order_date,
                shipping_name=customer.name,
                shipping_address='123 Farm Road',
                shipping_city=customer.city or 'Karachi',
                shipping_state='Sindh',
                shipping_phone='0300-1234567'
            )
            
            # Add 1-4 items to order
            num_items = random.randint(1, 4)
            order_products = random.sample(all_products, min(num_items, len(all_products)))
            
            subtotal = 0
            for product in order_products:
                quantity = random.randint(1, 5)
                unit_price = product.price
                total_price = unit_price * quantity
                subtotal += total_price
                
                order_item = OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    product_sku=product.sku,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                order.order_items.append(order_item)
            
            # Calculate totals
            order.subtotal = subtotal
            order.shipping_fee = 200 if subtotal < 5000 else 0
            order.tax_amount = subtotal * 0.05  # 5% tax
            order.total_amount = subtotal + order.shipping_fee + order.tax_amount
            
            db.session.add(order)
            orders_created += 1
    
    db.session.commit()
    print(f"Created {orders_created} sample orders.")
    print("Sample data seeded successfully!")


@app.cli.command()
def migrate_profile_fields():
    """Lightweight migration for profile-related columns.

    Adds columns if missing: profile_picture, profile_image, expertise_level.
    Works on SQLite using ALTER TABLE ADD COLUMN. Safe to re-run.
    """
    from sqlalchemy import inspect, text
    engine = db.engine
    insp = inspect(engine)
    existing = [col['name'] if isinstance(col, dict) else col.name for col in insp.get_columns('users')]
    statements = []
    if 'profile_picture' not in existing:
        statements.append("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255)")
    if 'profile_image' not in existing:
        statements.append("ALTER TABLE users ADD COLUMN profile_image VARCHAR(255)")
    if 'expertise_level' not in existing:
        statements.append("ALTER TABLE users ADD COLUMN expertise_level VARCHAR(20) DEFAULT 'beginner'")
    if not statements:
        print("No profile migration needed.")
        return
    with engine.connect() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                print(f"Executed: {stmt}")
            except Exception as e:
                print(f"Failed: {stmt} -> {e}")
    print("Profile field migration complete.")


@app.cli.command()
def migrate_new_tables():
    """Create newly added tables if they don't exist yet (idempotent).

    Currently ensures: blog_attachments, consultancy_messages
    """
    from sqlalchemy import inspect
    engine = db.engine
    insp = inspect(engine)
    created = []
    try:
        if not insp.has_table('blog_attachments'):
            BlogAttachment.__table__.create(engine)
            created.append('blog_attachments')
    except Exception as e:
        print(f"! Failed creating blog_attachments: {e}")
    try:
        if not insp.has_table('consultancy_messages'):
            ConsultancyMessage.__table__.create(engine)
            created.append('consultancy_messages')
    except Exception as e:
        print(f"! Failed creating consultancy_messages: {e}")
    if created:
        print("Created tables:", ", ".join(created))
    else:
        print("No new tables to create.")


@app.cli.command()
def seed_forum():
    """Seed forum with sample categories, threads, and replies."""
    from agrifarma.models.forum import Category, Thread, Reply
    from datetime import datetime, timedelta
    import random
    
    print("Seeding forum data...")
    
    # Check if categories already exist
    if Category.query.count() > 0:
        print("Forum categories already exist. Skipping...")
        return
    
    # Create main categories
    categories_data = [
        {
            'name': 'Crop Management',
            'slug': 'crop-management',
            'description': 'Discuss crop cultivation, disease management, and best practices',
            'icon': 'feather icon-aperture',
            'color': 'success',
            'position': 1
        },
        {
            'name': 'Equipment & Tools',
            'slug': 'equipment-tools',
            'description': 'Share knowledge about farming equipment, tools, and machinery',
            'icon': 'feather icon-tool',
            'color': 'info',
            'position': 2
        },
        {
            'name': 'Market Prices',
            'slug': 'market-prices',
            'description': 'Discuss market trends, prices, and selling strategies',
            'icon': 'feather icon-trending-up',
            'color': 'warning',
            'position': 3
        },
        {
            'name': 'General Discussion',
            'slug': 'general',
            'description': 'General agricultural topics and community discussions',
            'icon': 'feather icon-message-circle',
            'color': 'primary',
            'position': 4
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
        categories.append(category)
    
    db.session.flush()
    
    # Get some users for authorship
    farmers = User.query.join(Role).filter(Role.name == 'farmer').limit(5).all()
    if not farmers:
        print("No farmers found. Creating sample farmer...")
        farmer_role = Role.query.filter_by(name='farmer').first()
        sample_farmer = User(
            username='farmer_demo',
            name='Demo Farmer',
            email='farmer@demo.com',
            role_id=farmer_role.id,
            is_active=True
        )
        sample_farmer.set_password('password123')
        db.session.add(sample_farmer)
        db.session.flush()
        farmers = [sample_farmer]
    
    # Create threads
    threads_data = [
        ('Crop Management', 'Best practices for wheat cultivation in Sindh', 
         'I am planning to cultivate wheat this season. What are the best practices for wheat farming in Sindh climate? What seeds should I use?'),
        ('Crop Management', 'How to deal with cotton pest attack?',
         'My cotton crop is being attacked by whitefly. What organic pesticides would you recommend? Has anyone tried neem oil spray?'),
        ('Equipment & Tools', 'Which tractor brand is most reliable?',
         'Looking to buy a new tractor. What brands do you recommend for medium-sized farms? Budget is around 20-25 lakhs.'),
        ('Equipment & Tools', 'Water pump maintenance tips',
         'My diesel water pump is making unusual sounds. What could be the problem? How often should I service it?'),
        ('Market Prices', 'Current wheat prices in Hyderabad market',
         'What are the current wheat prices in Hyderabad mandi? Is it a good time to sell or should I wait?'),
        ('Market Prices', 'Rice export opportunities',
         'Anyone here exporting rice? What are the procedures and which countries are good markets for Pakistani rice?'),
        ('General Discussion', 'Government subsidy programs for farmers',
         'What subsidy programs are currently available for farmers in Sindh? How can we apply for them?'),
        ('General Discussion', 'Organic farming - worth it?',
         'Thinking about switching to organic farming. Is it profitable? What challenges should I expect?'),
    ]
    
    threads = []
    for cat_name, title, content in threads_data:
        category = next((c for c in categories if cat_name in c.name), categories[0])
        author = random.choice(farmers)
        
        # Create slug from title
        slug = title.lower().replace(' ', '-').replace('?', '').replace('!', '')[:50]
        
        thread = Thread(
            title=title,
            slug=slug,
            content=content,
            author_id=author.id,
            category_id=category.id,
            view_count=random.randint(10, 200),
            last_activity=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.session.add(thread)
        threads.append(thread)
    
    db.session.flush()
    
    # Create replies
    sample_replies = [
        'Thanks for sharing this information. Very helpful!',
        'I had the same issue last season. Try using...',
        'Good question! In my experience...',
        'This is what worked for me...',
        'I disagree. I think you should...',
        'Great discussion! My 2 cents:...',
        'Has anyone tried the alternative method?',
        'Update: I tried this and it worked!',
    ]
    
    for thread in threads:
        # Add 3-8 replies per thread
        num_replies = random.randint(3, 8)
        for i in range(num_replies):
            author = random.choice(farmers)
            reply = Reply(
                content=random.choice(sample_replies),
                author_id=author.id,
                thread_id=thread.id,
                created_at=thread.created_at + timedelta(hours=random.randint(1, 48))
            )
            db.session.add(reply)
            
            # Mark first reply as solution for 30% of threads
            if i == 0 and random.random() < 0.3:
                reply.is_solution = True
                thread.is_solved = True
    
    # Pin 1-2 threads
    for thread in random.sample(threads, 2):
        thread.is_pinned = True
    
    db.session.commit()
    print(f"✓ Created {len(categories)} categories")
    print(f"✓ Created {len(threads)} discussion threads")
    print(f"✓ Created replies for all threads")
    print("Forum seeding completed successfully!")


@app.cli.command()
def seed_blog():
    """Seed blog with sample categories, posts, and comments."""
    from agrifarma.models.blog import BlogCategory, BlogPost, BlogComment
    from datetime import datetime, timedelta
    import random
    
    print("Seeding blog data...")
    
    # Check if categories already exist
    if BlogCategory.query.count() > 0:
        print("Blog categories already exist. Skipping...")
        return
    
    # Create blog categories
    categories_data = [
        {
            'name': 'Farming Tips',
            'slug': 'farming-tips',
            'description': 'Practical farming advice and best practices',
            'icon': 'feather icon-book-open',
            'color': 'success',
            'position': 1
        },
        {
            'name': 'Crop Guides',
            'slug': 'crop-guides',
            'description': 'Complete guides for different crops',
            'icon': 'feather icon-layers',
            'color': 'info',
            'position': 2
        },
        {
            'name': 'Market Insights',
            'slug': 'market-insights',
            'description': 'Market trends and pricing analysis',
            'icon': 'feather icon-trending-up',
            'color': 'warning',
            'position': 3
        },
        {
            'name': 'Technology',
            'slug': 'technology',
            'description': 'Modern farming technology and innovations',
            'icon': 'feather icon-cpu',
            'color': 'primary',
            'position': 4
        },
    ]
    
    categories = []
    for cat_data in categories_data:
        category = BlogCategory(**cat_data)
        db.session.add(category)
        categories.append(category)
    
    db.session.flush()
    
    # Get authors (admin and consultants)
    admins = User.query.join(Role).filter(Role.name == 'admin').all()
    consultants = User.query.join(Role).filter(Role.name == 'consultant').all()
    authors = admins + consultants
    
    if not authors:
        print("No admin/consultant users found. Creating sample author...")
        admin_role = Role.query.filter_by(name='admin').first()
        sample_author = User(
            username='admin_blog',
            name='Blog Admin',
            email='blog@demo.com',
            role_id=admin_role.id,
            is_active=True
        )
        sample_author.set_password('password123')
        db.session.add(sample_author)
        db.session.flush()
        authors = [sample_author]
    
    # Sample blog posts data
    posts_data = [
        ('Farming Tips', '10 Essential Tips for Successful Wheat Farming in Sindh',
         'Discover the key practices that can help you maximize your wheat yield this season.',
         '''<h2>Introduction</h2>
         <p>Wheat farming in Sindh requires specific techniques to deal with local climate and soil conditions. Here are 10 essential tips every farmer should know.</p>
         <h3>1. Soil Preparation</h3>
         <p>Proper soil preparation is crucial. Test your soil pH and ensure it's between 6.0-7.5 for optimal wheat growth.</p>
         <h3>2. Seed Selection</h3>
         <p>Choose varieties suited to Sindh's climate. Popular options include TD-1 and Mehran-89.</p>
         <h3>3. Sowing Time</h3>
         <p>The best time for wheat sowing in Sindh is mid-November to early December.</p>''',
         'wheat,farming,tips,sindh'),
        
        ('Crop Guides', 'Complete Guide to Cotton Cultivation',
         'Everything you need to know about growing cotton successfully from planting to harvest.',
         '''<h2>Cotton Cultivation Basics</h2>
         <p>Cotton is one of Pakistan's major cash crops. This guide covers all aspects of cotton farming.</p>
         <h3>Soil Requirements</h3>
         <p>Cotton thrives in well-drained loamy soil with good organic content.</p>
         <h3>Irrigation</h3>
         <p>Cotton requires regular watering, especially during flowering and boll formation stages.</p>
         <h3>Pest Management</h3>
         <p>Watch out for cotton bollworms and whiteflies. Use integrated pest management strategies.</p>''',
         'cotton,guide,cultivation,crop'),
        
        ('Market Insights', 'Rice Export Market Trends 2025',
         'Analysis of current rice export opportunities and market prices for Pakistani farmers.',
         '''<h2>Global Rice Market Overview</h2>
         <p>Pakistani Basmati rice continues to have strong demand in international markets.</p>
         <h3>Current Prices</h3>
         <p>Export prices for Basmati rice have increased by 15% compared to last year.</p>
         <h3>Target Markets</h3>
         <p>Middle East and European markets are showing increased demand for quality rice.</p>''',
         'rice,export,market,prices'),
        
        ('Technology', 'Smart Irrigation Systems for Small Farms',
         'How modern irrigation technology can help save water and improve crop yields.',
         '''<h2>Benefits of Smart Irrigation</h2>
         <p>Smart irrigation systems use sensors and automation to optimize water usage.</p>
         <h3>Cost-Effective Solutions</h3>
         <p>Even small farms can benefit from affordable drip irrigation kits.</p>
         <h3>Water Conservation</h3>
         <p>Smart systems can reduce water usage by up to 40% while maintaining crop health.</p>''',
         'technology,irrigation,farming'),
        
        ('Farming Tips', 'Organic Pest Control Methods',
         'Natural and effective ways to control pests without harmful chemicals.',
         '''<h2>Why Choose Organic Pest Control?</h2>
         <p>Organic methods are safer for the environment and produce healthier crops.</p>
         <h3>Neem Oil Spray</h3>
         <p>Neem oil is effective against many common pests and is completely natural.</p>
         <h3>Companion Planting</h3>
         <p>Plant marigolds and basil alongside crops to naturally repel insects.</p>''',
         'organic,pest control,natural'),
        
        ('Crop Guides', 'Sugarcane Farming: Best Practices',
         'Maximize your sugarcane yield with these proven farming techniques.',
         '''<h2>Sugarcane Cultivation</h2>
         <p>Sugarcane is a profitable crop when grown using proper techniques.</p>
         <h3>Planting Season</h3>
         <p>February-March is ideal for spring planting in Sindh region.</p>
         <h3>Fertilizer Application</h3>
         <p>Apply nitrogen-rich fertilizers in split doses for best results.</p>''',
         'sugarcane,farming,cultivation'),
    ]
    
    posts = []
    for cat_name, title, excerpt, content, tags in posts_data:
        category = next((c for c in categories if cat_name in c.name), categories[0])
        author = random.choice(authors)
        
        slug = title.lower().replace(' ', '-').replace(':', '').replace('?', '')[:100]
        
        post = BlogPost(
            title=title,
            slug=slug,
            excerpt=excerpt,
            content=content,
            author_id=author.id,
            category_id=category.id,
            tags=tags,
            is_published=True,
            is_featured=random.random() < 0.4,  # 40% featured
            view_count=random.randint(50, 500),
            like_count=random.randint(5, 50),
            published_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.session.add(post)
        posts.append(post)
    
    db.session.flush()
    
    # Create comments
    sample_comments = [
        'Great article! Very informative.',
        'Thanks for sharing this valuable information.',
        'I tried this method and it worked perfectly!',
        'Can you provide more details about this?',
        'This helped me a lot. Keep posting!',
        'Excellent tips for farmers.',
        'I have a question about the implementation...',
        'Very useful content. Saved for future reference.',
    ]
    
    # Get some users for comments
    all_users = User.query.limit(10).all()
    if not all_users:
        all_users = authors
    
    for post in posts:
        # Add 2-6 comments per post
        num_comments = random.randint(2, 6)
        for i in range(num_comments):
            author = random.choice(all_users)
            comment = BlogComment(
                content=random.choice(sample_comments),
                author_id=author.id,
                post_id=post.id,
                is_approved=True,
                created_at=post.published_at + timedelta(days=random.randint(1, 30))
            )
            db.session.add(comment)
    
    db.session.commit()
    print(f"✓ Created {len(categories)} blog categories")
    print(f"✓ Created {len(posts)} blog posts")
    print(f"✓ Created comments for all posts")
    print("Blog seeding completed successfully!")


@app.cli.command()
def migrate_srs_tables():
    """Create SRS compliance tracking tables if they don't exist."""
    from sqlalchemy import inspect
    
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    tables_to_create = []
    
    if 'srs_modules' not in existing_tables:
        tables_to_create.append('srs_modules')
    
    if 'srs_requirements' not in existing_tables:
        tables_to_create.append('srs_requirements')
    
    if tables_to_create:
        # Import models to ensure they're registered
        from agrifarma.models.srs_compliance import SRSModule, SRSRequirement
        
        # Create only the missing tables
        db.create_all()
        
        print(f"Created tables: {', '.join(tables_to_create)}")
    else:
        print("All SRS compliance tables already exist.")


@app.cli.command()
def generate_srs_report():
    """Generate SRS compliance report."""
    from agrifarma.utils.srs_scanner import create_scanner
    import os
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    scanner = create_scanner(project_root)
    
    print("\n" + "="*60)
    print("  📊 SRS COMPLIANCE REPORT")
    print("="*60 + "\n")
    
    report = scanner.generate_report()
    
    print(f"Overall Completion: {report['summary']['overall_completion']}%")
    print(f"Completed Requirements: {report['summary']['completed_requirements']}/{report['summary']['total_requirements']}")
    print(f"Partial Requirements: {report['summary']['partial_requirements']}")
    print(f"Missing Requirements: {report['summary']['missing_requirements']}")
    print(f"\nModules: {report['summary']['completed_modules']}/{report['summary']['total_modules']} complete\n")
    
    print("-" * 60)
    for module in report['modules']:
        status_icon = {
            'completed': '✓',
            'partial': '⚠',
            'missing': '✗'
        }.get(module['status'], '?')
        
        print(f"{status_icon} {module['name']}: {module['completion']}% ({module['status'].upper()})")
    
    print("-" * 60)
    print(f"\nDetailed report available at: /admin/srs-status")
    print("="*60 + "\n")


@app.cli.command()
def show_missing_features():
    """Show missing and partial features with actionable details."""
    from agrifarma.utils.srs_scanner import create_scanner
    import os
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    scanner = create_scanner(project_root)
    report = scanner.generate_report()
    
    print("\n" + "="*60)
    print("  MISSING & INCOMPLETE FEATURES")
    print("="*60 + "\n")
    
    # Prioritize by module priority
    priority_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
    sorted_modules = sorted(report['modules'], 
                          key=lambda m: (priority_order.get(m['priority'], 5), -m['completion']))
    
    for module in sorted_modules:
        # Show only modules with missing/partial requirements
        incomplete_reqs = [r for r in module['requirements'] 
                          if r['status'] in ['missing', 'partial']]
        
        if not incomplete_reqs:
            continue
        
        print(f"\n{'='*60}")
        print(f"MODULE: {module['name']} ({module['completion']}%)")
        print(f"   Priority: {module['priority'].upper()}")
        print(f"   Status: {module['status'].upper()}")
        print(f"{'='*60}\n")
        
        for req in incomplete_reqs:
            status_icon = '[PARTIAL]' if req['status'] == 'partial' else '[MISSING]'
            print(f"{status_icon} {req['name']} ({req['completion']}%)")
            
            # Show what's missing
            if req['routes']['missing']:
                print(f"   Missing Routes:")
                for route in req['routes']['missing']:
                    print(f"      - {route}")
            
            if req['templates']['missing']:
                print(f"   Missing Templates:")
                for template in req['templates']['missing']:
                    print(f"      - {template}")
            
            if req['models']['missing']:
                print(f"   Missing Models:")
                for model in req['models']['missing']:
                    print(f"      - {model}")
            
            if req['keywords']['missing']:
                print(f"   Missing Code Patterns:")
                for keyword in req['keywords']['missing'][:3]:  # Show first 3
                    print(f"      - {keyword}")
            
            print()
    
    print("="*60)
    print("\nTIP: Run 'flask generate-srs-report' for summary")
    print("Dashboard: http://127.0.0.1:5000/admin/srs-status")
    print("="*60 + "\n")


@app.cli.command()
def srs_next_steps():
    """Show recommended next steps based on priority and completion."""
    from agrifarma.utils.srs_scanner import create_scanner
    import os
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    scanner = create_scanner(project_root)
    report = scanner.generate_report()
    
    print("\n" + "="*60)
    print("  RECOMMENDED NEXT STEPS")
    print("="*60 + "\n")
    
    # Find high-priority incomplete features
    critical_tasks = []
    high_tasks = []
    
    for module in report['modules']:
        if module['priority'] == 'critical' and module['completion'] < 100:
            for req in module['requirements']:
                if req['status'] != 'completed':
                    critical_tasks.append({
                        'module': module['name'],
                        'requirement': req['name'],
                        'completion': req['completion'],
                        'priority': 'CRITICAL',
                        'missing': len(req['routes']['missing']) + len(req['templates']['missing']) + len(req['models']['missing'])
                    })
        elif module['priority'] == 'high' and module['completion'] < 100:
            for req in module['requirements']:
                if req['status'] != 'completed':
                    high_tasks.append({
                        'module': module['name'],
                        'requirement': req['name'],
                        'completion': req['completion'],
                        'priority': 'HIGH',
                        'missing': len(req['routes']['missing']) + len(req['templates']['missing']) + len(req['models']['missing'])
                    })
    
    # Sort by completion (lowest first) and missing items (most first)
    critical_tasks.sort(key=lambda x: (x['completion'], -x['missing']))
    high_tasks.sort(key=lambda x: (x['completion'], -x['missing']))
    
    print("[CRITICAL PRIORITY] - Complete These First\n")
    for i, task in enumerate(critical_tasks[:5], 1):
        print(f"{i}. {task['requirement']}")
        print(f"   Module: {task['module']}")
        print(f"   Progress: {task['completion']}%")
        print(f"   Missing Components: {task['missing']}")
        print()
    
    if not critical_tasks:
        print("   All critical features complete!\n")
    
    print("\n[HIGH PRIORITY] - Do These Next\n")
    for i, task in enumerate(high_tasks[:5], 1):
        print(f"{i}. {task['requirement']}")
        print(f"   Module: {task['module']}")
        print(f"   Progress: {task['completion']}%")
        print(f"   Missing Components: {task['missing']}")
        print()
    
    if not high_tasks:
        print("   All high priority features complete!\n")
    
    print("="*60)
    print("\nTIP: Focus on completing one requirement at a time")
    print("Details: flask show-missing-features")
    print("="*60 + "\n")



if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🌾 AGRIFARMA SERVER 🌾")
    print("="*60)
    print(f"\n  ✓ Server URL: http://127.0.0.1:5000/")
    print(f"  ✓ Debug Mode: ON")
    print(f"  ✓ Auto-reload: DISABLED (for stability)")
    print("\n * Running on all addresses (0.0.0.0)")
    print(" * Running on http://127.0.0.1:5000")
    print("Press CTRL+C to quit")
    print("="*60 + "\n")
    
    # Run server WITHOUT reloader to avoid Windows port binding issues
    app.run(
        host='0.0.0.0',          # All interfaces pe listen kare
        port=5000,
        debug=True,
        use_reloader=False,      # ✓ DISABLED - Issue fix!
        use_debugger=True,       # Debug info milega
        threaded=True            # Multiple requests handle kare
    )
