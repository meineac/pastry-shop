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
    {
        "title": "New Summer Menu",
        "summary": "Refresh your summer palate with our handcrafted seasonal fruit tartlets, chilled elderflower mousselines, and sun-ripened organic berry creations.",
        "text": (
            "Summer at Pastry Shop is a celebration of vibrant colors and botanical fragrances harvested from small partner orchards. "
            "Our new tartlet crust is baked from stone-ground almond flour and French butter, delivering a rich sablé crumble that resists moisture.\n\n"
            "Beneath the glittering berry dome lies an infused crème diplomat perfumed with fresh garden lemon verbena leaves. "
            "Hand-placed redcurrants, blackberries, and wild woodland strawberries are then glazed with an organic elderflower reduction.\n\n"
            "Whether enjoyed on our sunny garden terrace or packed in our signature gift box, these seasonal creations bring refreshing acidity to warm afternoons. "
            "Pair them with our chilled hibiscus tea for the ultimate midday culinary indulgence."
        ),
    },
    {
        "title": "Award-Winning Pastry",
        "summary": "Our grand cru dark chocolate creation with roasted hazelnut praline won highest honors at the National Confectionery Guild championship.",
        "text": (
            "Designed over eight months of meticulous formulation, the Royal Truffle Entremet represents the pinnacle of modern French pastry artistry. "
            "At its core lies a flourless biscuit infused with single-origin Madagascan cacao nibs, delivering deep earthy undertones.\n\n"
            "Encasing the delicate sponge is a light-as-air dark chocolate mousse balanced with sea salt caramel and crunchy roasted Piedmont hazelnuts. "
            "The multi-layered cake is blasted to minus thirty degrees before taking its final bath in our obsidian cocoa mirror glaze.\n\n"
            "Food critics and guild judges unanimously praised the harmony of contrasting textures and the refined balance of cocoa acidity. "
            "The entremet is now available daily in our Baker Street showcase and for bespoke celebration pre-orders."
        ),
    },
    {
        "title": "Pastry Class Opening",
        "summary": "Step into our professional kitchen studio for hands-on intensive workshops guided step-by-step by master pâtissier Marie Leblanc herself.",
        "text": (
            "For the first time since our founding, Pastry Shop is opening its kitchen doors to amateur bakers and passionate food lovers. "
            "Our weekend masterclasses accommodate small groups of six students to guarantee personalized attention at every stage of preparation.\n\n"
            "Over two immersive days, participants will master the technical secrets of macaronage, silky fruit curds, and flaky puff pastry. "
            "Each student is provided with dedicated marble workstations, professional copper confectionery pots, and premium raw ingredients.\n\n"
            "Every participant takes home their own customized pastry showcase box along with our founder's hand-bound recipe compendium. "
            "Reservations open on the first Monday of every month through our website customer portal."
        ),
    },
    {
        "title": "Holiday Specials",
        "summary": "Celebrate festive gatherings with our limited-edition Bûches de Noël, spiced gingerbread entremets, and gold-leaf candied orange marzipan.",
        "text": (
            "The winter holiday season transforms our kitchen into a bustling workshop of traditional festive confectionery and sweet celebration. "
            "This year, our pastry brigade has prepared three distinct holiday logs designed to delight every member of your family gathering.\n\n"
            "Highlights include a dark cherry Valrhona yule log rolled in cocoa velvet and a roasted chestnut cream sponge soaked in rum syrup. "
            "Each centerpiece is crowned with hand-sculpted sugar mushrooms and glistening edible gold leaf imported from Florence.\n\n"
            "Holiday pre-orders are strictly limited to ensure uncompromising artisanal excellence in every single batch. "
            "Reserve your festive dessert today to guarantee delivery in time for Christmas Eve and New Year celebrations."
        ),
    },
    {
        "title": "New Collaboration",
        "summary": "Kyoto ceremonial matcha joins classic French viennoiserie in our exclusive cross-cultural partnership with heritage tea masters.",
        "text": (
            "True culinary innovation often sparks at the intersection of two storied gastronomic traditions honoring craft and contemplation. "
            "We have partnered with historic Uji tea producers to import first-harvest ceremonial matcha directly to our London bakehouse.\n\n"
            "Our signature matcha croissant features vibrant green laminations infused with earthy tea solids and filled with yuzu citrus ganache. "
            "The subtle savory astringency of stone-ground tencha leaves cuts beautifully through rich Normandy butter layers.\n\n"
            "This limited-edition collaboration will run throughout the coming season across all store locations. "
            "Stop by our café counter to experience this harmonious dialogue between Japanese tea culture and French pastry art."
        ),
    },
    {
        "title": "Sustainability Effort",
        "summary": "Discover how our direct fair-trade partnerships with local organic dairy farmers ensure uncompromised purity and ethical sustainability in every bite.",
        "text": (
            "True culinary craftsmanship begins long before flour meets water—it begins on pasture lands and fertile country soils. "
            "We have partnered with heritage dairy farms in Somerset that practice regenerative farming and pasture grazing throughout the year.\n\n"
            "Fresh heavy cream and golden butter arrive at our bakery doors within twenty-four hours of churning, preserving essential aromatics and live cultures. "
            "This pristine milk forms the foundation of our silky mousselines, ganaches, and slow-cultured brioche doughs.\n\n"
            "By paying fair premiums directly to smallholder farming families, we support sustainable agricultural practices while providing our guests with pure ingredients. "
            "Transparent food systems make every mouthful both delicious and responsible."
        ),
    },
    {
        "title": "Delivery Expanded",
        "summary": "Enjoy oven-fresh croissants, chilled entremets, and artisanal celebration cakes delivered directly to your doorstep with our temperature-controlled fleet.",
        "text": (
            "Getting warm morning pastries and delicate chilled mousse cakes safely across the city requires specialized delivery logistics. "
            "We are thrilled to unveil our dedicated electric courier fleet equipped with dual-zone climate-controlled compartments.\n\n"
            "Viennoiserie and warm breads travel in insulated gentle warming chambers, while delicate tarts and macarons remain chilled at four degrees. "
            "Real-time route optimization ensures your morning pastry arrives crisp, warm, and ready for breakfast within forty minutes of dispatch.\n\n"
            "The expanded delivery zone now covers all metropolitan districts seven days a week from seven in the morning until eight at night. "
            "Place your order through our simplified online checkout to experience bakery-fresh bliss in the comfort of your home."
        ),
    },
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
