"""
Seed script to add dummy forum threads with replies.
Run this after setting up the database.
"""
import sys
from datetime import datetime, timedelta
from app import app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.forum import Thread, Reply, Category


def seed_forum():
    """Add dummy forum threads with categories and replies."""
    
    with app.app_context():
        # Get or verify existing categories
        categories = Category.query.filter_by(is_active=True).all()
        
        if not categories:
            print("❌ No forum categories found. Please create categories first.")
            return
        
        print(f"✅ Found {len(categories)} forum categories")
        
        # Get some users for authors and commenters
        users = User.query.limit(10).all()
        if len(users) < 2:
            print("❌ Not enough users found. Please create more users first.")
            return
        
        authors = users[:5]
        repliers = users[2:]
        
        # Use first category or create a general one
        general_cat = categories[0]
        
        # Create forum threads
        forum_threads = [
            {
                'title': 'Best time to plant wheat in Hyderabad? (حیدرآباد میں گندم کب بوئیں؟)',
                'slug': 'best-time-plant-wheat-hyderabad',
                'content': '''I'm a farmer from Hyderabad and this will be my first year growing wheat. 
                
I've heard different opinions from fellow farmers - some say early November is best, others recommend waiting until late November or even early December.

What's your experience? When do you usually plant wheat in Hyderabad region? 

Also, which variety would you recommend for our climate? I'm considering TD-1 or Mehran-89.

Any advice would be greatly appreciated! شکریہ''',
                'author_id': authors[0].id,
                'category_id': general_cat.id,
                'is_pinned': True,
                'view_count': 156,
                'created_at': datetime.utcnow() - timedelta(days=20),
                'last_activity': datetime.utcnow() - timedelta(days=2),
            },
            {
                'title': 'Dealing with pink bollworm in cotton - need help!',
                'slug': 'pink-bollworm-cotton-help',
                'content': '''My cotton crop is being severely affected by pink bollworm this season. I've tried spraying twice with recommended pesticides but the problem persists.

Current situation:
- 15 acres of BT cotton (variety IUB-13)
- Planted in early May
- First spray: 15 days ago
- Second spray: 5 days ago
- Still seeing damaged bolls and larvae

What else can I do? Should I change the pesticide? Is there any biological control method that works?

I'm worried about my entire crop. Please share your experiences and solutions.''',
                'author_id': authors[1].id,
                'category_id': general_cat.id,
                'view_count': 203,
                'created_at': datetime.utcnow() - timedelta(days=15),
                'last_activity': datetime.utcnow() - timedelta(hours=8),
            },
            {
                'title': 'Drip irrigation vs flood irrigation - cost comparison?',
                'slug': 'drip-vs-flood-irrigation-cost',
                'content': '''I'm planning to switch from flood irrigation to drip irrigation for my 10-acre farm. I grow vegetables (tomatoes, chilies, cucumbers) mainly.

Questions:
1. What's the installation cost per acre for drip system?
2. How much water can I really save?
3. What about electricity costs for pumping?
4. Maintenance costs - are they high?
5. Any government subsidies available?

I've heard it pays for itself in 2-3 years. Can anyone who has made this switch share actual numbers?

Also, which brand do you recommend? I've seen Netafim, Jain, and some local brands.''',
                'author_id': authors[2].id,
                'category_id': general_cat.id,
                'view_count': 178,
                'created_at': datetime.utcnow() - timedelta(days=12),
                'last_activity': datetime.utcnow() - timedelta(days=1),
            },
            {
                'title': 'Rice yield very low this year - what went wrong?',
                'slug': 'low-rice-yield-problem',
                'content': '''I got only 25 maunds per acre this year from my rice crop, compared to 35-40 maunds in previous years. I'm trying to figure out what went wrong.

Details:
- Variety: Super Basmati
- Area: 8 acres in Badin district
- Used same fertilizer schedule as last year
- Transplanted in early July
- No major pest or disease problems
- Adequate irrigation

The crop looked healthy but the grain filling was poor. Grains are smaller than usual and many are empty.

Could it be a nutrient deficiency? Temperature stress? Something else?

Please help me understand so I can do better next season.''',
                'author_id': authors[3].id,
                'category_id': general_cat.id,
                'is_solved': True,
                'view_count': 134,
                'created_at': datetime.utcnow() - timedelta(days=10),
                'last_activity': datetime.utcnow() - timedelta(days=3),
            },
            {
                'title': 'Recommendations for 50 HP tractor under 15 lakh?',
                'slug': 'tractor-recommendations-50hp',
                'content': '''Looking to buy my first tractor for a 20-acre farm. Budget is 12-15 lakh rupees.

Requirements:
- 45-50 HP
- Good fuel efficiency
- Reliable brand with service center nearby (I'm in Nawabshah)
- Can handle both plowing and other implements

I've looked at:
- Massey Ferguson 240 
- New Holland 55-56
- Fiat 480

Which one would you recommend? Or any other options I should consider?

Also, should I buy new or 2-3 year old used tractor? What are the pros and cons?

Thanks in advance for your suggestions!''',
                'author_id': authors[4].id,
                'category_id': general_cat.id,
                'view_count': 245,
                'created_at': datetime.utcnow() - timedelta(days=8),
                'last_activity': datetime.utcnow() - timedelta(hours=5),
            },
            {
                'title': 'Organic farming - is it profitable in Pakistan?',
                'slug': 'organic-farming-profitability-pakistan',
                'content': '''I'm interested in converting my 5-acre farm to organic production. Growing vegetables and some fruits currently.

Main concerns:
1. Will the reduced yields make it unprofitable?
2. Where can I sell organic produce at premium prices?
3. Certification process - how difficult and expensive?
4. How to control pests without chemicals?
5. Organic fertilizer sources and costs?

Has anyone here successfully made the transition? What was your experience?

I'm in Karachi suburbs, so maybe I can target local organic food stores and restaurants.''',
                'author_id': authors[0].id,
                'category_id': general_cat.id,
                'view_count': 167,
                'created_at': datetime.utcnow() - timedelta(days=6),
                'last_activity': datetime.utcnow() - timedelta(hours=12),
            },
            {
                'title': 'Laser land leveling - worth the investment?',
                'slug': 'laser-land-leveling-worth-it',
                'content': '''I've heard a lot about laser land leveling and how it can improve water efficiency and crop yield.

My field is 25 acres with some uneven areas. Traditional leveling never gets it perfectly flat.

Questions:
- What's the cost per acre for laser leveling?
- How long does the leveling last before needing to be redone?
- What kind of improvement can I expect in water usage and yield?
- Any service providers in Sindh you can recommend?

Is it really worth the money or just hype? Looking for real experiences from farmers who have done it.''',
                'author_id': authors[1].id,
                'category_id': general_cat.id,
                'view_count': 98,
                'created_at': datetime.utcnow() - timedelta(days=4),
                'last_activity': datetime.utcnow() - timedelta(days=1),
            },
            {
                'title': 'Sugarcane price forecast for next season?',
                'slug': 'sugarcane-price-forecast',
                'content': '''Planning to plant sugarcane for the first time. Current support price is Rs. 300/40kg but I've heard it might increase next year.

Anyone have insights into:
- Expected support price for next crushing season?
- Which mills are paying on time?
- Is there going to be shortage or surplus?
- Better to plant now or wait?

I'm in Sanghar district with access to canal irrigation. Have 12 acres available for sugarcane.

Also, which variety should I plant? I've heard CPF-246 and SPF-213 are good.''',
                'author_id': authors[2].id,
                'category_id': general_cat.id,
                'view_count': 189,
                'created_at': datetime.utcnow() - timedelta(days=3),
                'last_activity': datetime.utcnow() - timedelta(hours=18),
            },
        ]
        
        # Add threads
        added_threads = []
        for thread_data in forum_threads:
            thread = Thread(**thread_data)
            db.session.add(thread)
            added_threads.append(thread)
            print(f"✅ Added thread: {thread.title}")
        
        db.session.commit()
        
        # Add replies to threads
        replies_data = [
            # Replies for wheat planting thread
            {
                'thread_idx': 0,
                'replies': [
                    {'content': 'Mid-November is ideal for Hyderabad. I plant around 15-20 November every year and get good results. TD-1 is excellent for our area!', 'days_after': 1},
                    {'content': 'I agree with the previous comment. Also make sure your soil is properly prepared. Do 2-3 plowings for fine tilth. یہ بہت ضروری ہے', 'days_after': 2},
                    {'content': 'Don\'t plant too early or aphids will be a problem. Wait until mid-November. Mehran-89 is also good but TD-1 gives slightly better yield.', 'days_after': 3},
                    {'content': 'Just remember to apply first irrigation 20-25 days after sowing. This is crucial for good germination and establishment.', 'days_after': 18},
                ]
            },
            # Replies for pink bollworm thread
            {
                'thread_idx': 1,
                'replies': [
                    {'content': 'Pink bollworm has developed resistance to many pesticides. Try Emamectin Benzoate or Chlorantraniliprole. These are more effective.', 'days_after': 0, 'hours_after': 6},
                    {'content': 'Also important: collect and destroy all damaged bolls. This reduces the population significantly. Do this manually every few days.', 'days_after': 1},
                    {'content': 'Use pheromone traps! They help monitor the moth population and catch many adults before they can lay eggs. Game changer for me.', 'days_after': 2},
                    {'content': 'I faced same problem last year. Switched to Spinosad-based pesticide and it worked well. But expensive compared to regular pesticides.', 'days_after': 3},
                    {'content': 'Deep plowing after harvest is essential. It exposes pupae to sun and birds. Prevention is better than cure!', 'days_after': 5},
                ]
            },
            # Replies for drip irrigation thread
            {
                'thread_idx': 2,
                'replies': [
                    {'content': 'I installed drip on 8 acres last year. Cost was Rs. 38,000 per acre for good quality system. Water saving is real - about 60% less water used.', 'days_after': 0, 'hours_after': 8},
                    {'content': 'Government subsidy available through Agriculture Department. You can get 40-50% subsidy in some districts. Check with your local office.', 'days_after': 1},
                    {'content': 'Maintenance is minimal. Just clean filters weekly and check for leaks. I spend maybe Rs. 2000-3000 per year on maintenance.', 'days_after': 2},
                    {'content': 'For vegetables, drip is definitely worth it. My tomato yield increased by 25% after switching. Plus you can do fertigation.', 'days_after': 10},
                ]
            },
            # Replies for rice yield thread
            {
                'thread_idx': 3,
                'replies': [
                    {'content': 'Sounds like zinc deficiency to me. Rice is very sensitive to zinc shortage. Did you apply zinc sulfate? It\'s crucial in our soils.', 'days_after': 0, 'hours_after': 4},
                    {'content': 'High temperatures during flowering can cause this. If it was too hot in August-September, that could explain empty grains.', 'days_after': 1},
                    {'content': 'SOLVED: Apply 10 kg zinc sulfate per acre before transplanting. Also use 25 kg per acre during land preparation. This should fix it.', 'days_after': 2},
                    {'content': 'Thanks everyone! I think it was both zinc deficiency AND heat stress. Will prepare better next season with zinc application.', 'days_after': 7, 'is_solution': True},
                ]
            },
            # Replies for tractor thread
            {
                'thread_idx': 4,
                'replies': [
                    {'content': 'Massey Ferguson 240 is very reliable. Parts easily available and fuel efficient. Running one for 5 years now, no major problems.', 'days_after': 0, 'hours_after': 3},
                    {'content': 'New Holland is more powerful but fuel consumption is higher. Depends on your soil type - heavy clay needs more power.', 'days_after': 0, 'hours_after': 8},
                    {'content': 'For 20 acres, 45-50 HP is good choice. I\'d suggest buying new rather than used. Warranty and peace of mind worth it.', 'days_after': 1},
                    {'content': 'Check if your local dealer has good service. I made mistake of buying without checking - nearest service center is 50 km away!', 'days_after': 2},
                    {'content': 'Banks give tractor loans at 12-13% markup. ZTBL rates are slightly better. Compare before deciding.', 'days_after': 7, 'hours_after': 20},
                ]
            },
            # Replies for organic farming thread
            {
                'thread_idx': 5,
                'replies': [
                    {'content': 'Organic farming is profitable if you have market access. In Karachi you can sell to organic stores at 50-100% premium over regular produce.', 'days_after': 0, 'hours_after': 6},
                    {'content': 'Certification costs around Rs. 50,000-100,000 initially. Annual inspection fees after that. Check with PCSIR or private certifiers.', 'days_after': 1},
                    {'content': 'For pest control, neem oil works well. Also companion planting and beneficial insects. It takes learning but definitely possible.', 'days_after': 2},
                ]
            },
            # Replies for laser leveling thread
            {
                'thread_idx': 6,
                'replies': [
                    {'content': 'Cost is Rs. 4000-5000 per acre. Leveling lasts 3-4 years easily. Water savings alone pay for it in 2 years.', 'days_after': 0, 'hours_after': 10},
                    {'content': 'I got 15-20% increase in wheat yield after laser leveling. Water distribution became uniform and no standing water in low areas.', 'days_after': 1},
                    {'content': 'Contact Agriculture Extension office. They have list of service providers with laser leveling equipment.', 'days_after': 3},
                ]
            },
            # Replies for sugarcane thread
            {
                'thread_idx': 7,
                'replies': [
                    {'content': 'Sugar mills are lobbying for Rs. 350/40kg support price. Might happen given rising input costs. But nothing confirmed yet.', 'days_after': 0, 'hours_after': 5},
                    {'content': 'Choose your mill carefully. Some mills delay payment by 6-8 months. Ask other farmers in your area about payment record.', 'days_after': 1},
                    {'content': 'CPF-246 is good for your area. High sugar content and disease resistant. Mature in 12-13 months.', 'days_after': 2},
                ]
            },
        ]
        
        total_replies = 0
        for reply_set in replies_data:
            thread = added_threads[reply_set['thread_idx']]
            for reply_data in reply_set['replies']:
                days = reply_data.get('days_after', 0)
                hours = reply_data.get('hours_after', 0)
                
                reply = Reply(
                    content=reply_data['content'],
                    author_id=repliers[total_replies % len(repliers)].id,
                    thread_id=thread.id,
                    is_solution=reply_data.get('is_solution', False),
                    created_at=thread.created_at + timedelta(days=days, hours=hours)
                )
                db.session.add(reply)
                total_replies += 1
        
        db.session.commit()
        
        # Update thread last_activity based on latest reply
        for thread in added_threads:
            latest_reply = Reply.query.filter_by(thread_id=thread.id, is_deleted=False)\
                .order_by(Reply.created_at.desc()).first()
            if latest_reply:
                thread.last_activity = latest_reply.created_at
        
        db.session.commit()
        
        print(f"\n🎉 Successfully added {len(added_threads)} forum threads!")
        print(f"💬 Added {total_replies} replies")
        print(f"📌 Pinned threads: {sum(1 for t in forum_threads if t.get('is_pinned', False))}")
        print(f"✅ Solved threads: {sum(1 for t in forum_threads if t.get('is_solved', False))}")
        print("\n💡 Tip: Visit /forum to see the discussions")


if __name__ == '__main__':
    try:
        seed_forum()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
