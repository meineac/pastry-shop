You need to implement a Django project according to the requirements below:

**1. GLOBAL TECHNICAL CONSTRAINTS (CRITICAL)**

- **Architecture:** STRICTLY use Function-Based Views (FBV). You are FORBIDDEN from using Class-Based Views (CBV) such as CreateView, UpdateView, ListView, DetailView, LoginView, etc. All logic, including authentication and registration, must be implemented via FBV.
- **Database:** Use SQLite for development.
- **Client side restrictions:** No usage of JavaScript is permitted.
- **URL Routing:** Use ONLY Regular Expressions for routing via `re_path()` or `url()`. Do NOT use standard `path()` with angle brackets.
- Create an abstract base model with the timestamp fields for `created_at` and `updated_at`. Inherit from this base model for your core entities, and use the standard `models.Model` for tags etc (where date is not and would not be needed.

**2. PROJECT REQUIREMENTS**

**1. Model Relationship Requirements**

Implement relationships:

- One-to-One (OneToOneField)
- One-to-Many (ForeignKey)
- Many-to-Many (ManyToManyField)

**2. CRUD Operations**

Implement CRUD (create, read, update, delete) operations for the core entities.

**3. Admin Panel**

- Add all models to the admin panel.
- Provide data management, filtering, and inline editing of related records.

**4. Authorization, Authentication, and Access Rights**

Implement authorization/authentication mechanisms and restrict access based on permissions:

- Admin (Superuser)
- Registered User (Staff)
- Registered User (Customer)
- Unregistered User

**5. Data Seeding**

Ensure data population for demonstration purposes. (Note: implement via a custom `populate_db.py` command).

**6. Third-party APIs**

Connect and use 2 third-party APIs:

- IPinfo
- OpenWeather

**7. Statistics and Analytics**

Display statistical metrics:

- List of clients/products in alphabetical order and total sales amount
- Statistical metrics (mean, mode, and median) for the sales amount.
- Statistical metrics (mean and median) for client age.
- Which product type is the most popular.
- Which product type generates the most profit.

**8. Dates, Time, and Timezones**

- Display the user's timezone and current date.
- Display the data addition/modification dates in tables for both the user's timezone and UTC.
- Display a calendar in text format.
- Dates must strictly be displayed in the (DD/MM/YYYY) format.

**9. Specific Data Requirements**

- Phone numbers must strictly be displayed in the format: +375 (29) XXX-XX-XX.
- Clients and staff must have an 18+ age restriction.

**10. Visualization and Interface**

- Implement visualization via a chart or graph to show the distribution of metrics by groups and/or changes in metrics by dates/groups.
- Form validation on both the server side and the client side.
- The appearance/design of the website is not important.

**11. Search and Sorting**

Implement search by any parameter and sorting of the displayed data.

**12. Testing and Logging**

- Add tests. Test coverage must be 80% or higher.
- Add logging.
- Ensure support for different logging levels (fetch from application configuration).

**13. Deployment and Infrastructure**

- Develop a Dockerfile and docker-compose file for local project launch (with public images for the project and database). (Note: PostgreSQL must be used here).
- Prepare the project for hosting on Render.

**3. SPECIFICATIONS**

Website: "Pastry Shop"

**Pages:**

- **Home:** Brief information about the latest published news. (Ability to click through to read the article).
- **User Location (determined via IPinfo):**
    - User's timezone
    - Current time for the user's timezone
    - Weather
- **About the Company:** Text (history by years, company details – database tables).
- **News:**
    - List of articles:
        - Content of a single list item: image, title, tags, date added, short description. ("Read" to open the full article).
    - Filter articles by tags.
    - Single search across any fields: tag, title, short description.
- **Vacancies:**
    - List of vacancies:
        - Content of a single list item: Vacancy title, tags, date updated, vacancy description.
    - Filter vacancies by tags.
    - Search across any fields: title, tag, description.
- **Q&A:**
    - List of frequently asked questions and answers with date added:
        - Content of a single list item: question, tags, date added, answer.
    - Filter questions by tags.
    - Search across any fields: question, tags, answer.
- **Contacts:**
    - List of employees:
        - Content of a single list item: employee photo, position, phone numbers, email.
- **Privacy Policy:** Blank page.
- **Reviews (specific reviews about service, the store, etc.):**
    - Content of a single list item: Username, tags (service, product quality, etc.), rating 0-5, text, date (database table).
    - "Add Review" button with redirection:
        - To the login window (if the user is not authenticated).
        - To the review creation form.
- **Promo Codes and Coupons:**
    - List of active and archived promo codes:
        - Content of a single list item: promo code, expiration date, conditions.
    - Sort by newest.
- **Catalog:**
    - List of products:
        - Content of a single list item: Photo, product name, category, product price.
        - Clicking a product redirects to the product card.
    - Filter by: price, category, manufacturer.
    - Search: by name, category.
    - "Add to Cart" button.
- **Product Card:**
    - Product photo
    - Name
    - Description:
        - Ingredients
        - Quantity by units of measurement (pieces, kilograms, liters).
    - Manufacturer.
    - Reviews (product reviews; a client can leave a review for a product only once and only after receiving the product).
- **Cart:**
    - List of items in the cart (content of a single list item is identical to the catalog list, but instead of "Add to Cart", there is a "Remove from Cart" button).
    - Checkout button: redirects to the checkout page.        
- **Checkout:**
    - Delivery address:
        - Store pickup: select a store from the list (price from the database).
        - Courier delivery: enter address (fixed price).
    - Payment by cash or card.
    - Promo code (check conditions to apply the promo code).
    - Total price including delivery.
    - "Place Order" button.
- **Profile (Client):**
    - User information:
        - User's name
        - Username
        - Date of birth
    - Current orders (orders with any status except 'finished').
    - Link to the user's order history page (all orders except current ones):
        - List of orders:
            - Content of a single list item: order number, price, creation date and modification date (received, canceled, etc.), status, "Details" button: redirects to the order's items.
            - Content of a single item in the order list is identical to the catalog list, but instead of "Add to Cart", there is a "Leave a Review" button.
- **Profile (Admin and Staff):**
    - User information:
        - Name
        - Username
        - Role (staff/admin)
        - Contact information
        - Registration date
- **Clients:**
    - List of clients:
        - Content of a single list item:
            - Name
            - Brief user statistics:
                - Number of received orders
                - Number of canceled orders
            - Button to open the client card
    - Search by name
    - Filter clients by: purchased product, product tag, date range of the last order.
    - "Add" button to save them to the list of clients you are working with.
- **Client Card (Admin and Staff):**
    - Client name
    - Age
    - Registration date
    - Contact information
    - List of client's orders
    - List of client's reviews
- **My Clients (Admin and Staff):**
    - List of clients you are working with (same as the "Clients" page, but with a "Remove" button instead of "Add").
- **Statistics (Admin and Staff):**
    - List of products:
        - For each product: product preview, number of reviews (for each rating and total count), number of sales.
        - Clicking redirects to the product card.
    - Statistical lists, sorted from best to worst:
        - Statistical metrics (mean, mode, and median) for sales amount.
        - Statistical metrics (mean and median) for client age.
        - Which product type is most popular.
        - Which product type generates the most profit.
    - Graphs (matplotlib):
        - Purchases of a specific product by date.
        - Purchases by product tag.
- **Staff - List of Employees (Admin):**
    - Content of a single list item:
        - Employee name
        - Username
        - Account creation date
        - "Revoke Access" button.

**4. USER PAGES ACCESS**

- **Administrator (Superuser):**
    - Home: View.
    - About the Company: Create, view, edit, hide, delete.
    - News: Create, view, edit, hide, delete.
    - Vacancies: Create, view, edit, hide, delete.
    - Q&A: Create, view, edit, hide, delete.
    - Contacts: View.
    - Privacy Policy: View.
    - Reviews: View.
    - Promo Codes and Coupons: Create, view, edit, hide, delete.
    - Catalog: Create, view, edit, hide, delete: products, product groups (tags), manufacturers.
        - Add product.
        - Add group and select products belonging to this group.
        - Add manufacturer and select products for this manufacturer (Warning: this will overwrite the manufacturer for all selected products).
    - Product Card: Edit product.
    - Admin does not have a cart.
    - Checkout: Since admin has no cart, they cannot place orders either.
    - Profile: View.
    - Clients: View.
    - Client Card: View.
    - My Clients: View.
    - Statistics: View (can select which products and tags to base graphs on; defaults to graphs of total product purchases by date and purchases by all tags).
    - Staff - List of Employees (Admin): Create, view, edit, revoke access, delete.
    - HAS ACCESS TO ADMIN PANEL WHICH MUST BE IMPLEMENTED ACCORDING TO PROJECT REQUIREMENTS
- **Registered User (Staff):**
    - Home: View.
    - About the Company: View.
    - News: View.
    - Vacancies: View.
    - Q&A: View.
    - Contacts: View.
    - Privacy Policy: View.
    - Reviews: View.
    - Promo Codes and Coupons: View.
    - Catalog: View.
    - Product Card: View.
    - Staff does not have a cart.
    - Checkout: Since staff has no cart, they cannot place orders either.
    - Profile: View.
    - Clients: View.
    - Client Card: View.
    - My Clients: View.
    - Statistics: View (can select which products and tags to base graphs on; defaults to graphs of total product purchases by date and purchases by all tags).
        
- **Registered User (Customer):**
    - Home: View.
    - About the Company: View.
    - News: View.
    - Vacancies: View.
    - Q&A: View.
    - Contacts: View.
    - Privacy Policy: View.
    - Reviews: View, add review. edit and delete their own reviews.
    - Promo Codes and Coupons: View.
    - Catalog: View.        
    - Product Card: View.
    - Cart: View, remove items, proceed to checkout.
    - Checkout.
    - Profile: View.
- **Unregistered User (Guest):** (Attempting to add a review or add an item to the cart must redirect to the registration page).
    - Home: View.
    - About the Company: View.
    - News: View.
    - Vacancies: View.
    - Q&A: View.
    - Contacts: View.
    - Privacy Policy: View.
    - Reviews: View.
    - Promo Codes and Coupons: View.        
    - Catalog: View.
    - Product Card: View.

**5. ENTITIES**

**1. Core Domain Entities (Catalog)**
- **Product:** Name, price, quantity, unit of measurement (pieces, kilograms, liters), photo, ingredients.
- **Category:** Product category.
- **Manufacturer:** Manufacturing company.

**2. Users and Accounts**

- **User:** Base model (custom), containing username, password, role (Admin, Staff, Customer).
- **Client (CustomerProfile):** Extension of the user, containing name, date of birth, contact phone number in +375 (29) XXX-XX-XX format, email, registration date.
- **Employee (StaffProfile):** Extension of the user, containing full name, position, photo, contact details, date of birth.

**3. Business Processes (Purchasing)**

- **Order:** Tracks the client, delivery type (courier/pickup), payment type, order status, creation, and modification dates.
- **OrderItem (Product in Order):** Intermediate model linking Order and Product, tracking the quantity of products in a specific order.
- **Cart:** Active shopping session of a client.
- **CartItem (Product in Cart):** Intermediate model linking Cart and Product, specifying the quantity.
- **PickupPoint:** Store address to select for delivery during checkout.
- **PromoCode:** Code, expiration date, status (active/archived), conditions of application.

**4. Content Management System (CMS)**

- **News (Article):** Title, image, short summary, full text, date added, links to tags. (News tags).
- **CompanyInfo:** Text information, history by years, company details.
- **Vacancy:** Title, description, date added, links to tags. (Vacancy tags).
- **QaA (Q&A):** Question text, answer text, date added, links to tags. (Q&A tags).
- **Review:** Author, rating (0-5), review text, date, links to tags. Can be linked to a specific product or the store as a whole. (Review tags).