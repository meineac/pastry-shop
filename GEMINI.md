# Pastry Shop — Project Constraints & Requirements

These rules apply to ALL work on this project. They are derived from the project requirements specification and must be followed at all times.

## Styling Constraint

- **NO CSS or other styles.** The project uses pure HTML and Python only.
- Do NOT add `style=` inline attributes, `<style>` blocks, CSS files, or `class=` attributes intended for styling.
- Use semantic HTML elements for visual meaning (e.g., `<strong>` instead of `style="font-weight:bold"`).

## Base Template Inheritance

- Every page template MUST extend either `core/base.html` or `core/base_auth.html`.
- This ensures a uniform site structure across all pages.

## No JavaScript (see also `.agents/rules/architecture-constraints.md`)

- Zero client-side JavaScript. No `<script>` tags, no inline event handlers.
- Interactive UI must use HTML-only mechanisms (`<details>/<summary>`, form submissions, anchors).

## HTML Markup Requirements

All templates must collectively demonstrate the following HTML elements. Weave them into pages where they fit thematically:

- **Metadata**: `<meta charset>`, `<meta name="viewport">`, `<meta name="description">`, `<meta name="keywords">`, `<link rel="icon">` in base template.
- **Microdata**: Schema.org attributes (`itemscope`, `itemtype`, `itemprop`) for search engine optimization.
- **Semantic text**: `<em>`, `<strong>`, `<mark>`, `<time datetime="...">`, `<address>`.
- **Specific tags**: `<code>`, `<abbr title="...">`, `<dfn>`, `<blockquote>`, `<q>`, `<cite>`, `<time>`.
- **Quatrain**: A text block formatted as a poem/quatrain using `<br>` (fixed breaks) and `<wbr>` (potential breaks).
- **Links**: Standard links, download links (`<a download>`), and in-page anchors (`<a href="#id">`).
- **Lists & figures**: `<ul>`, `<ol>`, `<dl>`, `<figure>`, `<figcaption>`.
- **Navigation**: Both horizontal navigation (header) and vertical navigation (footer or sidebar).
- **Data table**: At least one table with `<thead>`, `<tbody>`, header cells (`<th>`), merged cells (`colspan`/`rowspan`), and `headers` attribute. Do NOT use tables for layout.
- **Forms**: Use `<fieldset>/<legend>` containers, HTML5 validation attributes (`required`, `pattern`, `minlength`, `maxlength`, `min`, `max`), various `<input>` types, `<select>`, `<textarea>`, and `<button>`.
- **Embedded content**: `<iframe>` (e.g., Google Maps), `<video>`, `<audio>`.
- **Images**: All product/content images should use `<img>`. Responsive images (`srcset`, `sizes`) are a plus.
- **`<time>` elements**: All displayed dates must use `<time datetime="YYYY-MM-DD">DD/MM/YYYY</time>`.

## Mock Data

- Text seed data lives in `core/management/seed_data/`.
- Pre-generated images live in `media/` (products, news, staff_photos).
- New seed data for partners, banners, etc. should follow the same pattern.

## Database Tables Required

The following content types MUST be stored in the database (not hardcoded in templates):
- News/Articles
- Company Info (About Us)
- Q&A (FAQ)
- Contacts (via StaffProfile)
- Reviews
- Vacancies
- Promo Codes
- Partners (with logos and website URLs)
- Promotional Banners

## Page Content Requirements Summary

1. **Home**: logo, promotional banners, product catalog preview (few items + link to full catalog), latest article (title + summary), partner companies (logos + links).
2. **Product Detail**: item details + "Add to Cart" button.
3. **Cart**: listed items + "Checkout", "Remove", and "Increase/Decrease Quantity" controls.
4. **Payment**: handled within the existing checkout page (no separate page needed).
5. **About Us**: company info, video, logo, history timeline, business details, certificate (plain text only).
6. **News**: article list with title, summary, image, "Read More" button → full article.
7. **Q&A**: FAQ list with dates; click to reveal answer (use `<details>/<summary>`).
8. **Contacts**: employee photos, job descriptions, phone numbers, email addresses.
9. **Privacy Policy**: actual pastry-shop-themed content (not blank).
10. **Vacancies**: job openings with descriptions.
11. **Reviews**: reviewer name, rating, text, date. "Add Review" button → login redirect or review form (text field, rating selector, Submit).
12. **Promo Codes**: list separated into active and archived sections.

