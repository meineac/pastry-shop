"""
Management command: populate_db

Populates the database with demo data for the Pastry Shop project.
Run with:
    python manage.py populate_db

The command is idempotent — re-running it will not create duplicate records
because it uses ``get_or_create`` for every object.
"""

import logging
import re
import os
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from catalog.models import Category, Manufacturer, Product
from cms.models import CompanyInfo, News, Vacancy, QaA, Review
from users.models import User, CustomerProfile, StaffProfile
from purchasing.models import Order, OrderItem, PickupPoint, PromoCode

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

PICKUP_POINTS_DATA = [
    {"address": "123 Baker Street", "working_hours": "07:00 - 20:00", "price": "0.00"},
    {"address": "456 Pastry Lane", "working_hours": "08:00 - 21:00", "price": "5.00"},
    {"address": "789 Dessert Blvd", "working_hours": "09:00 - 18:00", "price": "3.50"},
]

MANUFACTURERS = [
    {"name": "PhlloCraft Wholesale", "description": "Premium, paper-thin phyllo and kataifi dough tailored for delicate Mediterranean pastries.", "contact_email": "trade@phyllocraft.com"},
    {"name": "CrispCrest Manufacturers", "description": "Industrial-scale producer of puff pastry ribbons and shells for commercial catering.", "contact_email": "volume@crispcrest.com"},
    {"name": "Glaze & Ganache Labs", "description": "B2B provider of technical pastry components like mirror glazes, stable mousses, and pralines.", "contact_email": "lab@glazeganache.com"},
    {"name": "AlpineDough Suppliers", "description": "Cold-chain distributor of traditional shortcrust, sablé, and savory pie crusts.", "contact_email": "sales@alpinedough.com"},
    {"name": "ButterGlow Pastries", "description": "Craft manufacturer dedicated exclusively to brioche dough variants and enriched sweet buns.", "contact_email": "supply@butterglow.com"},
    {"name": "SweetStratum Bakers", "description": "Multi-layered puff pastries and gourmet viennoiserie utilizing high-fat European butter.", "contact_email": "client@sweetstratum.com"},
    {"name": "VelvetBatter Creations", "description": "Premade premium sponge layers, génoise, and wet batters for upscale cake assembly.", "contact_email": "info@velvetbatter.com"},
    {"name": "PuffPerfect Mill", "description": "Focuses on organic, high-protein flour blends for ultra-light, structural choux pastry.", "contact_email": "baking@puffperfect.com"},
    {"name": "FlakyLayer Co.", "description": "High-volume supplier of flash-frozen croissant dough and danish bases for rapid baking.", "contact_email": "orders@flakylayer.com"},
    {"name": "GoldenCrust Artisans", "description": "Specializes in traditional, hand-laminated puff pastry sheets and pre-shaped tart shells.", "contact_email": "wholesale@goldencrust.com"},
]

CATEGORIES = [
    {"name": "Basics & Components", "description": "Prepared components like mirrors glazes, praline pastes, and stable pastry creams."},
    {"name": "Phyllo & Mediterranean", "description": "Paper-thin dough pastries including baklava, kataifi, and strudels."},
    {"name": "Batters & Loaves", "description": "Tea cakes, financiers, madeleines, and dense loaf cakes."},
    {"name": "Macarons & Mignardises", "description": "Delicate almond-meringue cookies and bite-sized petits fours."},
    {"name": "Savory Pastries", "description": "Meat pies, quiches, sausage rolls, and stuffed puff pastry parcels."},
    {"name": "Cakes & Entremets", "description": "Multi-layered mousse cakes, sponges, génoises, and structured gateaux."},
    {"name": "Puff Pastry Desserts", "description": "Flaky, multi-layered structures featuring mille-feuille, turnovers, and palmiers."},
    {"name": "Choux Pastry", "description": "Light, hollow pastry shells used for éclairs, profiteroles, and chouquettes."},
    {"name": "Tarts & Tartlets", "description": "Shortcrust and sablé shells filled with frangipane, pastry cream, or fresh fruit."},
    {"name": "Viennoiserie", "description": "Yeast-leavened, laminated doughs including croissants, danishes, and brioche."},
]

PRODUCTS_MD = """
### 1. Viennoiserie
| Butter Croissant | **GoldenCrust Artisans** | $2.50 | piece | Wheat flour, European butter (82% fat), water, sugar, yeast, salt, egg wash. |
| Raspberry Danish | **FlakyLayer Co.** | $3.20 | piece | Enriched flour, butter, raspberry filling (raspberries, sugar, pectin), yeast, salt. |
| Chocolate Almond Croissant | **PuffPerfect Mill** | $3.75 | piece | Wheat flour, butter, almond paste, dark chocolate chips, sugar, yeast, sliced almonds. |
| Classic Brioche Loaf | **VelvetBatter Creations** | $6.50 | kg | High-gluten flour, eggs, butter, sugar, milk, yeast, sea salt. |
| Cinnamon Swirl Bun | **SweetStratum Bakers** | $2.80 | piece | Flour, butter, brown sugar, cinnamon, milk, yeast, powdered sugar glaze. |
| Pain au Chocolat | **ButterGlow Pastries** | $3.00 | piece | Wheat flour, butter, dark chocolate batons (55% cacao), water, sugar, yeast, salt. |
| Savory Leek Danish | **AlpineDough Suppliers** | $3.50 | piece | Puff pastry dough, sautéed leeks, parmesan cheese, heavy cream, nutmeg, egg wash. |
| Kouign-Amann | **Glaze & Ganache Labs** | $4.00 | piece | Bread flour, salted butter, sugar, water, yeast. |
| Mini Viennoiserie Assortment | **CrispCrest Manufacturers** | $12.00 | kg | Wheat flour, butter, sugar, yeast, assorted fillings (chocolate, raisins, custard). |
| Apple Turnover | **PhlloCraft Wholesale** | $2.90 | piece | Phyllo dough, diced apples, cinnamon, sugar, cornstarch, butter. |

### 2. Tarts & Tartlets
| Glazed Strawberry Tart | **FlakyLayer Co.** | $4.50 | piece | Sablé shell (flour, butter, sugar, egg), pastry cream, fresh strawberries, apricot glaze. |
| Lemon Meringue Tartlet | **PuffPerfect Mill** | $4.25 | piece | Sweet pastry shell, lemon curd (lemon juice, eggs, sugar, butter), Italian meringue. |
| Chocolate Ganache Tart | **VelvetBatter Creations** | $5.00 | piece | Cocoa shortcrust shell, dark chocolate (64% cacao), heavy cream, butter, sea salt flakes. |
| Frangipane Pear Tart | **SweetStratum Bakers** | $22.00 | kg | Flour, butter, almond flour, eggs, sugar, poached pears, flaked almonds. |
| Salted Caramel Nut Tart | **ButterGlow Pastries** | $4.75 | piece | Shortcrust dough, sugar, heavy cream, butter, mixed nuts (walnuts, pecans, almonds). |
| Fresh Fruit Tart Base | **AlpineDough Suppliers** | $15.00 | kg | Pre-baked sweet shortcrust pastry dough (flour, butter, sugar, eggs, salt). |
| Passionfruit Mango Tart | **Glaze & Ganache Labs** | $5.50 | piece | Sweet crust, passionfruit curd, fresh mango cubes, neutral mirror glaze. |
| Mini Tart Shell Assortment | **CrispCrest Manufacturers** | $18.50 | kg | Wheat flour, vegetable shortening, sugar, eggs, salt, natural vanilla flavor. |
| Baklava Tartlet | **PhlloCraft Wholesale** | $4.00 | piece | Layered phyllo base, chopped pistachios, walnuts, honey syrup, cinnamon, butter. |
| Bourbon Pecan Tart | **GoldenCrust Artisans** | $4.80 | piece | Pastry shell, pecans, brown sugar, corn syrup, bourbon, butter, eggs. |

### 3. Choux Pastry
| Classic Vanilla Éclair | **PuffPerfect Mill** | $3.80 | piece | Choux paste (water, butter, flour, eggs), vanilla bean pastry cream, fondant icing. |
| Chocolate Profiteroles | **VelvetBatter Creations** | $14.00 | kg | Choux pastry shells, bittersweet chocolate filling, cocoa powder glaze. |
| Paris-Brest | **SweetStratum Bakers** | $5.50 | piece | Choux ring, praline mousseline cream, toasted flaked almonds, powdered sugar. |
| Craquelin Choux Puffs | **ButterGlow Pastries** | $2.00 | piece | Choux dough, crunchy craquelin topper (brown sugar, butter, flour), whipped cream. |
| Frozen Choux Shells | **AlpineDough Suppliers** | $11.50 | kg | Water, eggs, wheat flour, butter, salt. |
| Saint-Honoré Cake | **Glaze & Ganache Labs** | $28.00 | kg | Puff pastry base, choux profiteroles, caramelized sugar, crème chiboust. |
| Churros | **CrispCrest Manufacturers** | $8.00 | kg | Flour, water, vegetable oil, salt, cinnamon sugar coating. |
| Mediterranean Cheese Gougères | **PhlloCraft Wholesale** | $3.50 | piece | Choux pastry mixed with feta, graviera cheese, black pepper, and dill. |
| Coffee Éclair | **GoldenCrust Artisans** | $3.80 | piece | Choux paste, coffee-infused pastry cream, coffee fondant glaze. |
| Raspberry Rose Religeuse | **FlakyLayer Co.** | $5.00 | piece | Double-tiered choux paste, rose-flavored custard, raspberry glaze, white chocolate. |

### 4. Puff Pastry Desserts
| Traditional Mille-Feuille | **VelvetBatter Creations** | $4.90 | piece | Inverse puff pastry, vanilla bean pastry cream, marbled fondant sugar topper. |
| Raspberry Palmiers | **SweetStratum Bakers** | $12.50 | kg | Laminated dough, granulated sugar, freeze-dried raspberry powder. |
| Apple Chaussons | **ButterGlow Pastries** | $3.20 | piece | Puff pastry, spiced apple compote (apples, sugar, butter, vanilla). |
| Bulk Puff Pastry Sheets | **AlpineDough Suppliers** | $9.00 | kg | Wheat flour, pastry butter, water, salt. |
| Gâteau Saint-Epvre | **Glaze & Ganache Labs** | $24.00 | kg | Laminated puff layers, meringue, hazelnut nougatine cream. |
| Vol-au-Vent Shells | **CrispCrest Manufacturers** | $15.00 | kg | Wheat flour, vegetable margarine, water, salt, egg wash. |
| Savory Spinach Puff | **PhlloCraft Wholesale** | $3.40 | piece | Flaky pastry, spinach, feta cheese, onions, olive oil, garlic. |
| Cinnamon Palmiers | **GoldenCrust Artisans** | $11.00 | kg | Flour, butter, sugar, cinnamon, salt. |
| Cherry Turnovers | **FlakyLayer Co.** | $3.10 | piece | Puff pastry, sour cherry filling, tapioca starch, coarse sugar crystals. |
| Vol-au-Vent Shell (Large) | **PuffPerfect Mill** | $2.50 | piece | Flour, high-fat butter, water, sea salt. |

### 5. Cakes & Entremets
| Triple Chocolate Entremet | **SweetStratum Bakers** | $6.50 | piece | Dark, milk, and white chocolate mousses, chocolate biscuit jaconde, mirror glaze. |
| Velvet Sponge Layers | **ButterGlow Pastries** | $13.50 | kg | Wheat flour, sugar, whole eggs, baking powder, vanilla extract. |
| Opera Cake | **AlpineDough Suppliers** | $5.80 | piece | Almond sponge cake dipped in coffee syrup, ganache, coffee buttercream, glaze. |
| Mango Passion Fruit Mousse | **Glaze & Ganache Labs** | $32.00 | kg | Mango purée, passion fruit juice, heavy cream, gelatin, sugar, sponge base. |
| Sheet Sponge Cake | **CrispCrest Manufacturers** | $10.00 | kg | Wheat flour, sugar, egg powder, emulsifiers, vanilla flavor. |
| Honey Walnut Cake Layers | **PhlloCraft Wholesale** | $14.00 | kg | Flour, honey, sugar, eggs, ground walnuts, baking soda. |
| Red Velvet Cake Sheet | **GoldenCrust Artisans** | $15.00 | kg | Flour, sugar, cocoa powder, buttermilk, butter, red food coloring. |
| Strawberry Fraisier | **FlakyLayer Co.** | $5.50 | piece | Génoise sponge, mousseline cream, fresh strawberries, marzipan topper. |
| Hazelnut Dacquoise | **PuffPerfect Mill** | $6.00 | piece | Hazelnut meringue layers, praline buttercream, toasted hazelnuts. |
| Matcha Green Tea Entremet | **VelvetBatter Creations** | $6.20 | piece | Matcha sponge, white chocolate matcha mousse, red bean paste insert. |

### 6. Savory Pastries
| Quiche Lorraine | **ButterGlow Pastries** | $4.50 | piece | Shortcrust pastry, heavy cream, eggs, smoked bacon lardons, gruyère cheese. |
| Classic Sausage Rolls | **AlpineDough Suppliers** | $12.00 | kg | Puff pastry, seasoned ground pork, sage, onions, breadcrumbs. |
| Beef & Mushroom Pie | **Glaze & Ganache Labs** | $5.50 | piece | Shortcrust base, puff pastry lid, diced beef, button mushrooms, red wine gravy. |
| Cocktail Savory Mix | **CrispCrest Manufacturers** | $16.00 | kg | Wheat flour, margarine, assorted fillings (cheese, spinach, minced beef). |
| Spanakopita Triangles | **PhlloCraft Wholesale** | $3.80 | piece | Phyllo dough, spinach, feta cheese, green onions, dill, olive oil, melted butter. |
| Chicken Pot Pie Base | **GoldenCrust Artisans** | $14.50 | kg | Savory shortcrust dough (flour, lard, butter, water, salt). |
| Spinach & Ricotta Plait | **FlakyLayer Co.** | $3.90 | piece | Puff pastry, chopped spinach, ricotta cheese, nutmeg, parmesan. |
| Goat Cheese & Tomato Tart | **PuffPerfect Mill** | $4.20 | piece | Puff pastry, goat cheese log slices, cherry tomatoes, thyme, olive oil. |
| Ham & Cheese Croissant | **VelvetBatter Creations** | $4.00 | piece | Laminated croissant dough, sliced smoked ham, swiss cheese, béchamel sauce. |
| Salmon Coulibiac | **SweetStratum Bakers** | $26.00 | kg | Puff pastry, salmon fillet, rice, hard-boiled eggs, mushrooms, dill. |

### 7. Macarons & Mignardises
| Salted Caramel Macarons | **AlpineDough Suppliers** | $45.00 | kg | Almond flour, powdered sugar, egg whites, sugar, heavy cream, butter, sea salt. |
| Raspberry Petit Four | **Glaze & Ganache Labs** | $1.80 | piece | Almond sponge, raspberry jam filling, white chocolate coating, fondant décor. |
| Assorted Macaron Shells | **CrispCrest Manufacturers** | $38.00 | kg | Ground almonds, sugar, egg white powder, food colorings. |
| Almond Baklava Bites | **PhlloCraft Wholesale** | $1.50 | piece | Phyllo layers, ground almonds, sugar syrup, orange blossom water, butter. |
| Pistachio Macaron | **GoldenCrust Artisans** | $2.00 | piece | Almond flour, egg whites, sugar, pistachio paste, white chocolate ganache. |
| Chocolate Ganache Macaron | **FlakyLayer Co.** | $2.00 | piece | Almond flour, cocoa powder, egg whites, sugar, dark chocolate cream. |
| Coconut Macaroons | **PuffPerfect Mill** | $14.00 | kg | Shredded coconut, egg whites, sugar, vanilla extract, dark chocolate drizzle. |
| Vanilla Bean Petit Four | **VelvetBatter Creations** | $1.95 | piece | Butter cake sponge, vanilla buttercream, white fondant dip. |
| Assorted Mignardises Box | **SweetStratum Bakers** | $22.00 | kg | Assorted bite-sized tarts, mini éclairs, and chocolate truffles. |
| Lemon Macaron | **ButterGlow Pastries** | $2.00 | piece | Almond flour, sugar, egg whites, lemon curd, lemon zest. |

### 8. Batters & Loaves
| Lemon Poppyseed Loaf | **Glaze & Ganache Labs** | $8.50 | kg | Wheat flour, sugar, eggs, butter, lemon juice, poppyseeds, baking powder. |
| Traditional Madeleines | **CrispCrest Manufacturers** | $14.00 | kg | Flour, sugar, eggs, butter, honey, lemon zest. |
| Almond Financiers | **PhlloCraft Wholesale** | $2.20 | piece | Beurre noisette (browned butter), egg whites, powdered sugar, almond flour, wheat flour. |
| Marble Cake Loaf | **GoldenCrust Artisans** | $9.00 | kg | Flour, butter, sugar, eggs, cocoa powder, vanilla extract, milk. |
| Blueberry Muffin Batter | **FlakyLayer Co.** | $6.00 | liter | Flour, sugar, vegetable oil, eggs, buttermilk, baking soda, frozen blueberries. |
| Chocolate Chip Loaf | **PuffPerfect Mill** | $8.80 | kg | Flour, butter, brown sugar, eggs, semi-sweet chocolate chunks. |
| Premium Brownie Batter | **VelvetBatter Creations** | $8.50 | liter | Melted dark chocolate, butter, sugar, eggs, cocoa powder, flour. |
| Orange Almond Loaf | **SweetStratum Bakers** | $10.00 | kg | Almond meal, sugar, eggs, whole boiled oranges, baking powder. |
| Buttermilk Pancake Batter | **ButterGlow Pastries** | $5.00 | liter | Buttermilk, flour, sugar, eggs, melted butter, baking powder, salt. |
| Classic Pound Cake | **AlpineDough Suppliers** | $9.50 | kg | Equal parts flour, butter, sugar, and whole eggs; vanilla extract. |

### 9. Phyllo & Mediterranean
| Bulk Phyllo Dough Sheets | **CrispCrest Manufacturers** | $7.50 | kg | Wheat flour, water, cornstarch, wheat starch, preservative. |
| Shredded Kataifi Dough | **PhlloCraft Wholesale** | $8.50 | kg | Wheat flour, water, salt, cornstarch, vegetable oil. |
| Pistachio Baklava | **GoldenCrust Artisans** | $28.00 | kg | Phyllo sheets, clarified butter, chopped pistachios, sugar, lemon syrup. |
| Apple Strudel | **FlakyLayer Co.** | $4.50 | piece | Thin phyllo dough, sliced apples, raisins, breadcrumbs, cinnamon, sugar, butter. |
| Galaktoboureko | **PuffPerfect Mill** | $5.00 | piece | Phyllo pastry layers, semolina custard filling, scented sugar syrup. |
| Cheese Bougatsa | **VelvetBatter Creations** | $4.20 | piece | Phyllo wrapper, mizithra and feta cheese blend, eggs, white pepper, butter. |
| Sweet Custard Bougatsa | **SweetStratum Bakers** | $4.50 | piece | Phyllo pastry, creamy semolina custard, powdered sugar, cinnamon dusting. |
| Tiropita (Cheese Pie) | **ButterGlow Pastries** | $3.50 | piece | Layered phyllo pastry, feta, ricotta, eggs, olive oil, white pepper. |
| Walnut Baklava Diamonds | **AlpineDough Suppliers** | $26.00 | kg | Phyllo dough, walnuts, butter, sugar, cloves, honey syrup. |
| Mediterranean Date Rolls | **Glaze & Ganache Labs** | $1.80 | piece | Phyllo pastry, pureed date paste, cardamom, orange blossom water, butter. |

### 10. Basics & Components
| Pastry Cream Mix | **PhlloCraft Wholesale** | $9.00 | kg | Sugar, modified starch, whey powder, dextrose, vanilla flavor, beta-carotene. |
| Neutral Mirror Glaze | **GoldenCrust Artisans** | $8.50 | liter | Water, sugar, glucose syrup, gelling agent (pectin), citric acid. |
| Liquid Egg Wash Blend | **FlakyLayer Co.** | $6.00 | liter | Pasteurized whole eggs, pasteurized egg yolks, salt, water. |
| Stabilized Whipping Cream | **PuffPerfect Mill** | $7.00 | liter | Heavy cream (36% milkfat), skim milk powder, stabilizers (carrageenan). |
| Dark Chocolate Mirror Glaze | **VelvetBatter Creations** | $11.50 | liter | Sugar, water, cocoa powder, dark chocolate, heavy cream, gelatin. |
| Pistachio Paste 100% | **SweetStratum Bakers** | $42.00 | kg | 100% lightly roasted peeled pistachios. |
| Hazelnut Praline Paste | **ButterGlow Pastries** | $35.00 | kg | Roasted hazelnuts (50%), sugar (50%), soy lecithin. |
| Vanilla Bean Pastry Cream | **AlpineDough Suppliers** | $10.50 | liter | Whole milk, sugar, egg yolks, cornstarch, butter, Bourbon vanilla bean paste. |
| Dark Chocolate Ganache 2:1 | **Glaze & Ganache Labs** | $14.00 | kg | Belgian dark chocolate (60% cacao), heavy cream (35% fat). |
| Royal Icing Mix | **CrispCrest Manufacturers** | $5.50 | kg | Powdered sugar, dried egg white powder, cornstarch, cream of tartar, vanilla. |
"""

UNIT_MAP = {
    "piece": Product.UnitMeasurement.PIECES,
    "kg": Product.UnitMeasurement.KILOGRAMS,
    "liter": Product.UnitMeasurement.LITERS,
}

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
    {"title": "Vegan Options", "summary": "Delicious plant-based treats.", "text": "We've expanded our menu to include 100% vegan cakes, cookies, and croissants without compromising taste."}
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
    {"title": "Assistant Baker", "desc": "Entry-level position for an enthusiastic learner."}
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
    {"q": "Do you cater events?", "a": "We offer wholesale and catering options for events of all sizes."}
]

# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Populate the database with comprehensive demo data including users, orders, news, and cms data."

    @transaction.atomic
    def handle(self, *args, **options):
        self._populate_company_info()
        self._populate_news()
        self._populate_vacancies()
        self._populate_qna()

        self.stdout.write("Populating manufacturers...")
        self._populate_manufacturers()

        self.stdout.write("Populating categories...")
        self._populate_categories()

        self.stdout.write("Populating products...")
        self._populate_products()

        self.stdout.write("Populating superuser...")
        self._populate_superuser()

        self.stdout.write("Populating staff...")
        self._populate_staff()

        self.stdout.write("Populating pickup points...")
        self._populate_pickup_points()

        self.stdout.write("Populating promocodes...")
        self._populate_promocodes()

        self.stdout.write("Populating customers, reviews, and orders...")
        self._populate_customers_and_orders()

        self.stdout.write(self.style.SUCCESS("Database successfully populated!"))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _populate_company_info(self):
        if not CompanyInfo.objects.exists():
            CompanyInfo.objects.create(
                text_information="We are a premium pastry shop dedicated to high-quality ingredients.",
                history_by_years="2010: Founded.\n2015: Opened flagship store.\n2022: Expanded city-wide.",
                company_details="Registration No: 123456789. Address: 123 Baker Street."
            )
            logger.info("Created Company Info.")

    def _populate_news(self):
        for item in NEWS_ITEMS:
            News.objects.get_or_create(
                title=item["title"],
                defaults={
                    "short_summary": item["summary"],
                    "full_text": item["text"]
                }
            )
        logger.info("Created 10 News records.")

    def _populate_vacancies(self):
        for item in VACANCIES:
            Vacancy.objects.get_or_create(
                title=item["title"],
                defaults={"description": item["desc"]}
            )
        logger.info("Created 10 Vacancies.")

    def _populate_qna(self):
        for item in QNA_ITEMS:
            QaA.objects.get_or_create(
                question_text=item["q"],
                defaults={"answer_text": item["a"]}
            )
        logger.info("Created 10 Q&A records.")

    def _populate_manufacturers(self):
        for data in MANUFACTURERS:
            Manufacturer.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "contact_email": data["contact_email"],
                },
            )

    def _populate_categories(self):
        for data in CATEGORIES:
            Category.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"]},
            )

    def _populate_products(self):
        current_category = None
        count = 0
        for line in PRODUCTS_MD.splitlines():
            line = line.strip()
            if not line: continue
            cat_match = re.match(r"### \d+\.\s+(.*)", line)
            if cat_match:
                category_name = cat_match.group(1).strip()
                try:
                    current_category = Category.objects.get(name=category_name)
                except Category.DoesNotExist:
                    current_category = None
                continue

            if line.startswith("|") and not line.startswith("| ---") and not line.startswith("| Product Name"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) != 5: continue
                name, manufacturer_name, price, unit_str, ingredients = parts
                manufacturer_name = manufacturer_name.replace("**", "")
                price = price.replace("$", "")

                try:
                    manufacturer = Manufacturer.objects.get(name=manufacturer_name)
                except Manufacturer.DoesNotExist:
                    continue

                unit = UNIT_MAP.get(unit_str, Product.UnitMeasurement.PIECES)
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "price": price,
                        "quantity": 100,
                        "unit_of_measurement": unit,
                        "ingredients": ingredients,
                        "category": current_category,
                        "manufacturer": manufacturer,
                        "is_active": True,
                    },
                )
                count += 1
        return count

    def _populate_superuser(self):
        su_username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        su_email = os.environ.get('SUPERUSER_EMAIL', 'admin@example.com')
        su_password = os.environ.get('SUPERUSER_PASSWORD', 'adminpass')
        if not User.objects.filter(username=su_username).exists():
            User.objects.create_superuser(
                username=su_username,
                email=su_email,
                password=su_password
            )
            logger.info("Created superuser from .env variables.")

    def _populate_staff(self):
        for i in range(1, 11):
            username = f"staffuser{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"staff{i}@pastry.com",
                    "role": User.Role.STAFF
                }
            )
            if created:
                user.set_password('staffpass123')
                user.save()
                StaffProfile.objects.create(
                    user=user,
                    position="Pastry Shop Employee",
                    contact_details=f"Phone: +375 (29) 222-22-{i:02d}",
                    date_of_birth=date(1990, 1, 1)
                )

    def _populate_pickup_points(self):
        for data in PICKUP_POINTS_DATA:
            PickupPoint.objects.get_or_create(
                address=data["address"],
                defaults={
                    "working_hours": data["working_hours"],
                    "price": data["price"]
                }
            )
        logger.info("Created Pickup Points.")

    def _populate_promocodes(self):
        for i in range(1, 11):
            code = f"PROMO{i * 10}"
            PromoCode.objects.get_or_create(
                code=code,
                defaults={
                    "expiration_date": date.today() + timedelta(days=365),
                    "discount_percentage": Decimal(random.randint(5, 20)),
                    "minimum_purchase_amount": Decimal(random.randint(10, 50)),
                    "conditions_of_application": "Standard discount",
                }
            )
        logger.info("Created 10 PromoCodes.")

    def _populate_customers_and_orders(self):
        products = list(Product.objects.all())
        pickup_points = list(PickupPoint.objects.all())
        if not products:
            logger.warning("No products available to generate orders.")
            return

        for i in range(1, 21):
            username = f"customer{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"customer{i}@pastry.com",
                    "role": User.Role.CUSTOMER
                }
            )
            if created:
                user.set_password('customerpass123')
                user.save()

                profile, _ = CustomerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "date_of_birth": date(1995, 5, 15),
                        "phone_number": f"+375 (29) 111-11-{i:02d}"
                    }
                )

                # 1 Review per customer
                Review.objects.create(
                    author=user,
                    rating=random.randint(4, 5),
                    review_text="Amazing pastry shop! I come here all the time.",
                    product=None
                )

                # 10 Purchases per customer
                for j in range(10):
                    order = Order.objects.create(
                        client=profile,
                        delivery_type=Order.DeliveryType.PICKUP,
                        pickup_point=random.choice(pickup_points) if pickup_points else None,
                        payment_type=Order.PaymentType.CARD,
                        status=Order.OrderStatus.COMPLETED,
                        final_price=0 
                    )
                    
                    num_items = random.randint(1, 3)
                    selected_products = random.sample(products, num_items)
                    total_price = Decimal(0)
                    
                    for prod in selected_products:
                        qty = random.randint(1, 4)
                        OrderItem.objects.create(
                            order=order,
                            product=prod,
                            quantity=qty,
                            purchase_price=prod.price,
                            historical_product_name=prod.name
                        )
                        total_price += prod.price * qty

                    order.final_price = total_price
                    # Backdate the order artificially
                    order.created_at = timezone.now() - timedelta(days=random.randint(1, 365))
                    order.save()