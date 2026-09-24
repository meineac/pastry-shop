"""
Seed data for the cms app: company info, news, vacancies, Q&A, partners, and banners.
"""

COMPANY_INFO = {
    "text_information": (
        "We are a premium pastry shop dedicated to high-quality ingredients and authentic French techniques. "
        "Every item in our showcase is crafted with care by our team of trained pâtissiers."
    ),
    "history_by_years": (
        "2010: Founded by Marie Leblanc in a small kitchen on Baker Street.\n"
        "2013: Won first regional award for our signature chocolate entremet.\n"
        "2015: Opened the flagship store at 123 Baker Street.\n"
        "2018: Launched city-wide delivery and online ordering.\n"
        "2020: Introduced our vegan and plant-based pastry range.\n"
        "2022: Expanded to three city locations.\n"
        "2025: Certified by the International Pastry Institute."
    ),
    "company_details": (
        "Registration No: 123456789. "
        "Address: 123 Baker Street, London, UK. "
        "VAT No: GB-987654321. "
        "Opening hours: Monday–Saturday 07:00–20:00."
    ),
    "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "certificate_text": (
        "CERTIFICATE OF QUALITY\n"
        "Pastry Shop — 123 Baker Street, London\n\n"
        "This certificate confirms that Pastry Shop meets all requirements of the\n"
        "International Pastry Standards Council (IPSC) for the production and sale\n"
        "of baked goods and confectionery.\n\n"
        "Certificate No: IPSC-2025-00342\n"
        "Issued: 01/06/2025\n"
        "Valid until: 01/06/2027\n"
        "Issuing body: International Pastry Standards Council\n"
        "Certification level: Gold"
    ),
}

PARTNERS = [
    {"name": "FreshFarm Dairy", "website": "https://freshfarmdairy.example.com", "logo": "partners/freshfarm_dairy.jpg"},
    {"name": "Organic Flour Mills", "website": "https://organicflour.example.com", "logo": "partners/organic_flour_mills.jpg"},
    {"name": "CacaoSource Premium", "website": "https://cacaosource.example.com", "logo": "partners/cacaosource_premium.jpg"},
    {"name": "Alpine Butter Co.", "website": "https://alpinebutter.example.com", "logo": "partners/alpine_butter_co.jpg"},
    {"name": "BerryBest Farms", "website": "https://berrybestfarms.example.com", "logo": "partners/berrybestfarms.jpg"},
]

BANNERS = [
    {"title": "Summer Collection", "image": "banners/summer_collection.jpg", "position": 1},
    {"title": "Holiday Specials", "image": "banners/holiday_specials.jpg", "position": 2},
    {"title": "New Arrivals", "image": "banners/new_arrivals.jpg", "position": 3},
]

NEWS_ITEMS = [
    {"title": "New Summer Menu", "summary": "Refresh yourself with our new fruit tarts.", "text": "We are launching a new lineup of summer fruit tarts packed with seasonal berries and tropical flavors."},
    {"title": "Award-Winning Pastry", "summary": "Our signature chocolate entremet won gold.", "text": "We are proud to announce our chocolate entremet took first place at the national pastry competition."},
    {"title": "Pastry Class Opening", "summary": "Learn the secrets of French baking.", "text": "Join our master bakers for an intensive weekend course on lamination and viennoiserie."},
    {"title": "Holiday Specials", "summary": "Pre-order your yule logs now.", "text": "The holiday season is here! Secure your festive treats including our famous Bûche de Noël."},
    {"title": "New Collaboration", "summary": "Matcha meets classic French techniques.", "text": "We've partnered with a premium tea supplier to bring you a unique line of matcha-infused pastries."},
    {"title": "Sustainability Effort", "summary": "Moving to 100% organic flour.", "text": "As part of our commitment to the environment, all our products now use locally sourced, organic flour."},
    {"title": "Delivery Expanded", "summary": "We now deliver city-wide.", "text": "You can now enjoy our pastries delivered directly to your door anywhere in the metropolitan area."},
    {"title": "Store Renovation", "summary": "A fresh look for our flagship store.", "text": "We've updated our dining area to provide a more comfortable and modern experience for our guests."},
    {"title": "Loyalty Program", "summary": "Earn points on every purchase.", "text": "Sign up for our new rewards program and earn free pastries, coffee, and exclusive discounts."},
    {"title": "Vegan Options", "summary": "Delicious plant-based treats.", "text": "We've expanded our menu to include 100% vegan cakes, cookies, and croissants without compromising taste."},
]

VACANCIES = [
    {"title": "Head Baker", "desc": "Looking for an experienced Head Baker to lead our morning team."},
    {"title": "Pastry Chef", "desc": "Seeking a creative Pastry Chef skilled in entremets and macarons."},
    {"title": "Cashier", "desc": "Friendly face needed for front-of-house operations."},
    {"title": "Barista", "desc": "Coffee enthusiast required to pair perfect brews with our pastries."},
    {"title": "Store Manager", "desc": "Experienced manager to oversee daily operations and staff."},
    {"title": "Delivery Driver", "desc": "Reliable driver for morning wholesale and retail deliveries."},
    {"title": "Marketing Intern", "desc": "Creative individual to help manage our social media presence."},
    {"title": "Dishwasher", "desc": "Essential team member to keep our bustling kitchen clean."},
    {"title": "Cake Decorator", "desc": "Detail-oriented decorator for custom event cakes."},
    {"title": "Assistant Baker", "desc": "Entry-level position for an enthusiastic learner."},
]

QNA_ITEMS = [
    {"q": "What are your hours?", "a": "We are open Monday to Saturday from 7:00 AM to 8:00 PM."},
    {"q": "Do you deliver?", "a": "Yes, we offer city-wide delivery for all our products."},
    {"q": "Are there vegan options?", "a": "Absolutely, we have a dedicated section for vegan pastries."},
    {"q": "Do you do custom cakes?", "a": "Yes, please contact us at least 48 hours in advance for custom orders."},
    {"q": "Is there a loyalty program?", "a": "Yes! Ask our cashiers to sign up and start earning points."},
    {"q": "Do you sell gift cards?", "a": "Gift cards are available in-store and online."},
    {"q": "Are pets allowed?", "a": "We welcome service animals indoors, and all pets on our outdoor patio."},
    {"q": "Do you use organic flour?", "a": "Yes, 100% of our flour is organic and locally sourced."},
    {"q": "Can I order in advance?", "a": "Yes, you can pre-order via our website or over the phone."},
    {"q": "Do you cater events?", "a": "We offer wholesale and catering options for events of all sizes."},
]
