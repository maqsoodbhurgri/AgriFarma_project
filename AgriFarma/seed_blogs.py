"""
Seed script to add dummy blog posts with comments.
Run this after setting up the database.
"""
import sys
from datetime import datetime, timedelta
from app import app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.blog import BlogPost, BlogCategory, BlogComment, BlogLike


def seed_blogs():
    """Add dummy blog posts with categories and comments."""
    
    with app.app_context():
        # Find or create blog categories
        categories_data = [
            {'name': 'Crop Management', 'slug': 'crop-management', 'description': 'Tips for managing different crops'},
            {'name': 'Soil & Fertilizers', 'slug': 'soil-fertilizers', 'description': 'Soil health and fertilization techniques'},
            {'name': 'Pest Control', 'slug': 'pest-control', 'description': 'Organic and chemical pest control methods'},
            {'name': 'Irrigation', 'slug': 'irrigation', 'description': 'Modern irrigation techniques'},
            {'name': 'Farm Equipment', 'slug': 'farm-equipment', 'description': 'Agricultural machinery and tools'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat = BlogCategory.query.filter_by(slug=cat_data['slug']).first()
            if not cat:
                cat = BlogCategory(**cat_data)
                db.session.add(cat)
                categories[cat_data['slug']] = cat
                print(f"✅ Created category: {cat.name}")
            else:
                categories[cat_data['slug']] = cat
                print(f"ℹ️  Category exists: {cat.name}")
        
        db.session.commit()
        
        # Get some users for authors and commenters
        users = User.query.limit(5).all()
        if not users:
            print("❌ No users found. Please create users first.")
            return
        
        author = users[0]
        commenters = users[1:] if len(users) > 1 else users
        
        # Delete existing blog posts to avoid duplicates
        BlogPost.query.delete()
        db.session.commit()
        print("🗑️  Cleared existing blog posts")
        
        # Create blog posts
        blog_posts = [
            {
                'title': 'Complete Guide to Wheat Farming in Sindh (سندھ میں گندم کی کاشت)',
                'slug': 'wheat-farming-guide-sindh',
                'excerpt': 'Learn the best practices for wheat cultivation in Sindh, from soil preparation to harvest. Includes tips on irrigation, fertilization, and disease management.',
                'content': '''<h2>Introduction to Wheat Farming</h2>
<p>Wheat is one of the most important crops in Sindh, Pakistan. With proper cultivation techniques, farmers can achieve yields of 40-50 maunds per acre.</p>

<h3>Soil Preparation</h3>
<p>Start by plowing the field 2-3 times to achieve fine tilth. The soil should be well-drained and rich in organic matter. Add farmyard manure at 10-15 tons per acre.</p>

<h3>Seed Selection and Sowing</h3>
<p>Choose certified seeds of varieties like TD-1, Anmol-91, or Mehran-89. Sow at a rate of 40-50 kg per acre. The ideal sowing time is mid-November to early December.</p>

<h3>Irrigation Management</h3>
<p>Wheat requires 4-5 irrigations depending on soil type and weather. First irrigation should be 20-25 days after sowing, followed by irrigations at tillering, jointing, flowering, and grain filling stages.</p>

<h3>Fertilizer Application</h3>
<p>Apply NPK fertilizers based on soil test results. Generally, use 60-80 kg nitrogen, 40-60 kg phosphorus, and 20-30 kg potash per acre.</p>

<h3>Pest and Disease Control</h3>
<p>Watch for aphids, stem borers, and rust diseases. Use recommended pesticides when pest population crosses economic threshold levels.</p>

<h3>Harvesting</h3>
<p>Harvest when grains turn golden yellow and moisture content is around 12-14%. Use combine harvester or traditional methods depending on field size.</p>''',
                'category_id': categories['crop-management'].id,
                'author_id': author.id,
                'featured_image': 'images/products/wheat-seeds.jpg',
                'tags': 'wheat, farming, sindh, crops, cultivation',
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow() - timedelta(days=15),
                'view_count': 234,
                'like_count': 45,
            },
            {
                'title': 'Organic Fertilizers: Benefits and Application Methods',
                'slug': 'organic-fertilizers-guide',
                'excerpt': 'Discover the advantages of organic fertilizers over chemical ones. Learn how to make compost at home and apply it effectively to your crops.',
                'content': '''<h2>Why Choose Organic Fertilizers?</h2>
<p>Organic fertilizers improve soil structure, increase water retention, and provide slow-release nutrients to plants. They also enhance beneficial microorganism activity in soil.</p>

<h3>Types of Organic Fertilizers</h3>
<ul>
<li><strong>Farmyard Manure (FYM):</strong> Well-decomposed animal waste, rich in nutrients</li>
<li><strong>Compost:</strong> Decomposed organic matter from kitchen and farm waste</li>
<li><strong>Green Manure:</strong> Crops grown specifically to be plowed back into soil</li>
<li><strong>Vermicompost:</strong> Earthworm-processed organic matter</li>
</ul>

<h3>Making Compost at Home</h3>
<p>1. Collect organic waste (vegetable peels, leaves, grass clippings)<br>
2. Create alternating layers of green and brown materials<br>
3. Keep moisture level like a wrung-out sponge<br>
4. Turn pile every 2 weeks<br>
5. Compost ready in 2-3 months</p>

<h3>Application Guidelines</h3>
<p>Apply organic fertilizers 2-3 weeks before planting to allow decomposition. Use 10-20 tons per acre for field crops and 5-10 tons for vegetables.</p>''',
                'category_id': categories['soil-fertilizers'].id,
                'author_id': author.id,
                'featured_image': 'images/products/organic-fertilizer.jpg',
                'tags': 'organic, fertilizer, compost, soil health',
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow() - timedelta(days=10),
                'view_count': 189,
                'like_count': 38,
            },
            {
                'title': 'Drip Irrigation: Save Water and Increase Yield',
                'slug': 'drip-irrigation-benefits',
                'excerpt': 'Drip irrigation can save up to 70% water compared to flood irrigation. Learn installation, maintenance, and cost-benefit analysis.',
                'content': '''<h2>What is Drip Irrigation?</h2>
<p>Drip irrigation is a modern method that delivers water directly to plant roots through a network of pipes and emitters. It's highly efficient and suitable for water-scarce regions.</p>

<h3>Advantages</h3>
<ul>
<li>Saves 50-70% water compared to flood irrigation</li>
<li>Reduces weed growth between crop rows</li>
<li>Allows precise fertilizer application (fertigation)</li>
<li>Suitable for uneven terrain</li>
<li>Prevents soil erosion and nutrient leaching</li>
</ul>

<h3>System Components</h3>
<p><strong>Main Line:</strong> PVC pipes carrying water from source<br>
<strong>Sub-main Lines:</strong> Smaller pipes distributing water<br>
<strong>Lateral Lines:</strong> Drip tubes with emitters<br>
<strong>Filters:</strong> Remove particles that can clog emitters<br>
<strong>Fertilizer Tank:</strong> For nutrient injection</p>

<h3>Installation Cost</h3>
<p>For 1 acre: Rs. 35,000 - 50,000 depending on quality. Government subsidies available in some areas. Payback period: 2-3 years through water and fertilizer savings.</p>

<h3>Maintenance</h3>
<p>Clean filters weekly, flush lateral lines monthly, and check for leaks regularly. Replace damaged emitters promptly.</p>''',
                'category_id': categories['irrigation'].id,
                'author_id': author.id,
                'featured_image': 'images/products/drip-irrigation.jpg',
                'tags': 'irrigation, drip, water saving, modern farming',
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow() - timedelta(days=7),
                'view_count': 156,
                'like_count': 32,
            },
            {
                'title': 'Integrated Pest Management for Cotton Crops',
                'slug': 'cotton-pest-management',
                'excerpt': 'Control cotton pests effectively using IPM approach. Reduce pesticide costs and environmental impact while protecting yields.',
                'content': '''<h2>Understanding IPM</h2>
<p>Integrated Pest Management (IPM) combines cultural, biological, and chemical methods to control pests economically while minimizing environmental risks.</p>

<h3>Common Cotton Pests in Sindh</h3>
<ul>
<li>Pink Bollworm</li>
<li>American Bollworm</li>
<li>Whitefly</li>
<li>Jassids (Leafhoppers)</li>
<li>Thrips</li>
</ul>

<h3>Cultural Control Methods</h3>
<p>1. Crop rotation with non-host crops<br>
2. Deep plowing after harvest to expose pupae<br>
3. Remove crop residues promptly<br>
4. Plant early to avoid peak pest pressure<br>
5. Use resistant varieties like BT cotton</p>

<h3>Biological Control</h3>
<p>Encourage natural predators like ladybugs, lacewings, and parasitic wasps. Avoid broad-spectrum insecticides that kill beneficial insects.</p>

<h3>Chemical Control</h3>
<p>Use pesticides only when pest population exceeds economic threshold levels. Rotate pesticide classes to prevent resistance. Follow label instructions strictly.</p>

<h3>Monitoring</h3>
<p>Scout fields 2-3 times per week. Use pheromone traps to monitor adult moth populations. Keep records of pest levels and control measures.</p>''',
                'category_id': categories['pest-control'].id,
                'author_id': author.id,
                'featured_image': 'images/products/pesticide-spray.jpg',
                'tags': 'pest control, IPM, cotton, insects',
                'is_published': True,
                'published_at': datetime.utcnow() - timedelta(days=5),
                'view_count': 98,
                'like_count': 21,
            },
            {
                'title': 'Choosing the Right Tractor for Your Farm',
                'slug': 'tractor-buying-guide',
                'excerpt': 'Complete buyer\'s guide for tractors. Compare horsepower, features, and brands to find the perfect tractor for your farm size and budget.',
                'content': '''<h2>Tractor Selection Guide</h2>
<p>Selecting the right tractor is crucial for farm productivity. Consider farm size, soil type, and crops when making your decision.</p>

<h3>Horsepower Requirements</h3>
<ul>
<li><strong>Small farms (5-10 acres):</strong> 25-35 HP</li>
<li><strong>Medium farms (10-25 acres):</strong> 40-50 HP</li>
<li><strong>Large farms (25+ acres):</strong> 60-75 HP or more</li>
</ul>

<h3>Popular Brands in Pakistan</h3>
<p><strong>Millat Tractors:</strong> Massey Ferguson models, reliable and fuel-efficient<br>
<strong>Al-Ghazi Tractors:</strong> New Holland series, powerful and durable<br>
<strong>Fiat Tractors:</strong> Affordable options for small farmers<br>
<strong>Chinese Brands:</strong> Budget-friendly but check parts availability</p>

<h3>Key Features to Consider</h3>
<ul>
<li>Engine power and fuel efficiency</li>
<li>Transmission type (manual vs. power steering)</li>
<li>Hydraulic lift capacity</li>
<li>PTO (Power Take-Off) options</li>
<li>Tire type and size</li>
<li>Warranty and after-sales service</li>
</ul>

<h3>Financing Options</h3>
<p>Many banks offer tractor financing at 12-15% markup. ZTBL (Zarai Taraqiati Bank) provides agricultural loans. Some dealers offer installment plans.</p>

<h3>Maintenance Tips</h3>
<p>Regular oil changes (every 100-150 hours), air filter cleaning, and proper storage extend tractor life. Budget 10-15% of purchase price annually for maintenance.</p>''',
                'category_id': categories['farm-equipment'].id,
                'author_id': author.id,
                'featured_image': 'images/products/tractor.jpg',
                'tags': 'tractor, machinery, equipment, farming',
                'is_published': True,
                'published_at': datetime.utcnow() - timedelta(days=3),
                'view_count': 145,
                'like_count': 28,
            },
            {
                'title': 'Rice Cultivation Calendar for Sindh Farmers',
                'slug': 'rice-cultivation-calendar',
                'excerpt': 'Month-by-month guide to rice farming. Know exactly when to perform each farming activity for maximum yield.',
                'content': '''<h2>Rice Farming Timeline</h2>
<p>Rice is a water-intensive crop requiring careful timing of operations. Follow this calendar for best results in Sindh region.</p>

<h3>April-May: Land Preparation</h3>
<p>• Plow field and level properly<br>
• Build bunds to hold water<br>
• Apply farmyard manure (8-10 tons/acre)</p>

<h3>May-June: Nursery Preparation</h3>
<p>• Prepare nursery bed (1/10th of main field)<br>
• Sow seeds at 25-30 kg per acre of nursery<br>
• Keep nursery bed moist</p>

<h3>June-July: Transplanting</h3>
<p>• Transplant 25-30 day old seedlings<br>
• Space: 20cm between rows, 15cm between plants<br>
• Maintain 2-3 inches standing water</p>

<h3>July-August: Growth Stage</h3>
<p>• First nitrogen application (50% of total)<br>
• Weed control manually or herbicide<br>
• Maintain water level 2-4 inches</p>

<h3>August-September: Flowering</h3>
<p>• Second nitrogen dose (remaining 50%)<br>
• Monitor for diseases (blast, sheath blight)<br>
• Control stem borers if threshold crossed</p>

<h3>October: Pre-Harvest</h3>
<p>• Drain field 10-15 days before harvest<br>
• Grain moisture should reach 20-22%</p>

<h3>November: Harvesting</h3>
<p>• Cut when 80% grains turn golden<br>
• Thresh and dry to 12-14% moisture<br>
• Store in dry, clean bags</p>''',
                'category_id': categories['crop-management'].id,
                'author_id': author.id,
                'featured_image': 'images/products/rice-seeds.jpg',
                'tags': 'rice, cultivation, calendar, sindh',
                'is_published': True,
                'published_at': datetime.utcnow() - timedelta(days=1),
                'view_count': 67,
                'like_count': 15,
            },
        ]
        
        # Add blog posts
        added_posts = []
        for post_data in blog_posts:
            post = BlogPost(**post_data)
            db.session.add(post)
            added_posts.append(post)
            print(f"✅ Added post: {post.title}")
        
        db.session.commit()
        
        # Add comments to blog posts
        comment_texts = [
            "Very informative article! Thanks for sharing these tips.",
            "I tried this method last season and got excellent results.",
            "Can you provide more details about the cost involved?",
            "This is exactly what I was looking for. Great work!",
            "Do you have any recommendations for small-scale farmers?",
            "What about the water requirements? Please clarify.",
            "Excellent guide! Shared with my fellow farmers.",
            "The pictures really help understand the process better.",
            "Would this work in other provinces too or just Sindh?",
            "Thanks! This saved me a lot of money on fertilizers.",
        ]
        
        total_comments = 0
        for i, post in enumerate(added_posts):
            # Add 2-5 comments per post
            num_comments = min(3 + i, len(commenters) * 2)
            for j in range(num_comments):
                if j < len(comment_texts):
                    comment = BlogComment(
                        content=comment_texts[j % len(comment_texts)],
                        author_id=commenters[j % len(commenters)].id,
                        post_id=post.id,
                        is_approved=True,
                        created_at=post.published_at + timedelta(days=j+1, hours=j*3)
                    )
                    db.session.add(comment)
                    total_comments += 1
        
        db.session.commit()
        
        print(f"\n🎉 Successfully added {len(added_posts)} blog posts!")
        print(f"💬 Added {total_comments} comments")
        print(f"📊 Featured posts: {sum(1 for p in blog_posts if p.get('is_featured', False))}")
        print("\n💡 Tip: Visit /blogs to see the articles")


if __name__ == '__main__':
    try:
        seed_blogs()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
