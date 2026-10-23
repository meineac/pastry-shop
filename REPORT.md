Analyzed main.css:L4070-4160
Analyzed main.css:L1311-1410
Analyzed main.css:L1411-1490
Analyzed base.html:L1-35
Analyzed home.html:L10-60
Analyzed home.html:L260-277
Analyzed about.html:L1-100
Analyzed about.html:L101-200
Analyzed about.html:L201-233
Analyzed news_list.html:L1-60
Analyzed news_list.html:L61-88
Analyzed news_detail.html:L1-50
Analyzed qna_list.html:L30-70
Analyzed contacts.html:L30-71
Analyzing vacancies.html:L35-85
Ran find vacancies template
Analyzed vacancies_list.html:L35-80
Ran find review templates · Exited with code 1
Ran find review and promo templates
Ran find all cms templates
Analyzed reviews_list.html:L1-50
Analyzed review_create.html:L1-25
Analyzed promo_codes.html:L1-70
Analyzed privacy_policy.html:L1-70

# Comprehensive Requirement Implementation Guide

This guide provides an exhaustive, line-by-line verification and explanation of every requirement implemented across the **Pastry Shop** project. All styles reside exclusively in custom CSS stylesheets and semantic HTML5 templates without any third-party UI frameworks, styling CDNs, or JavaScript scripts.

---

## 1. Constraints

### 1.1 No Styling Libraries & Disallow External Bootstrap CDN
* **Requirement**: Do not include styling libraries in the project. Disable `https://www.bootstrapcdn.com` if present.
* **Implementation**:
  - The project utilizes pure bespoke CSS written from scratch in [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css).
  - No CSS frameworks (such as Bootstrap, Tailwind CSS, or Foundation) or external CDN styling links exist anywhere in the codebase.
  - In [`core/templates/core/base.html#L10-L15`](file:///home/meineac/pastry-shop/core/templates/core/base.html#L10-L15), only the Google Fonts service and the local custom stylesheet `main.css` are linked:

```html
<!-- core/templates/core/base.html (Lines 10-15) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    <title>{% block title %}Pastry Shop{% endblock %}</title>
</head>
```

### 1.2 Base Template Inheritance
* **Requirement**: Base template inheritance across all pages.
* **Implementation**: Every template extends [`core/base.html`](file:///home/meineac/pastry-shop/core/templates/core/base.html) (or `core/base_auth.html`), guaranteeing consistent semantic structure and layout hierarchy across the entire website.

### 1.3 Certificate Ornate Ticket Structure
* **Requirement**: If the certificate was used as a simple graphic image, create a ticket or something similar that meets the requirements for a certificate.
* **Implementation**:
  - Implemented in [`cms/templates/cms/about.html#L211-L227`](file:///home/meineac/pastry-shop/cms/templates/cms/about.html#L211-L227) as an ornate ticket container utilizing SVG border slices, radial gradient, and watermark layering rather than a plain image:

```html
<!-- cms/templates/cms/about.html (Lines 211-227) -->
    {% if company_info.certificate_text %}
    <section id="certificate" aria-labelledby="certificate-heading" class="certificate-section">
        <h2 id="certificate-heading">Quality Certificate</h2>
        <div class="certificate-ticket-container">
            <div class="certificate-watermark" aria-hidden="true"></div>
            <div class="certificate-inner">
                <div class="certificate-badge">★ OFFICIAL CERTIFICATE OF ACCREDITATION ★</div>
                <pre class="certificate-text">{{ company_info.certificate_text }}</pre>
                <div class="certificate-footer">
                    <span>IPSC STANDARD COMPLIANT</span>
                    <span>ISSUED: 2026</span>
                </div>
            </div>
        </div>
    </section>
    {% endif %}
```

---

## 2. Selectors

### 2.1 Elements, Classes, and Attribute Selectors (`^=`, `$=`, `*=`)
* **Requirement**: Selectors using elements, classes, and attributes (starts with, ends with, or contains a specific value).
* **Implementation**: [`static/css/main.css#L180-L212`](file:///home/meineac/pastry-shop/static/css/main.css#L180-L212)

```css
/* static/css/main.css (Lines 180-212) */
/* Starts with mailto: */
a[href^="mailto:"]::before {
  content: "✉";
  margin-right: 0.45rem;
  font-size: 0.9em;
  text-decoration: none;
  display: inline-block;
}

/* Starts with tel: */
a[href^="tel:"]::before {
  content: "✆";
  margin-right: 0.45rem;
  font-size: 0.9em;
  text-decoration: none;
  display: inline-block;
}

/* Ends with .pdf */
a[href$=".pdf"]::after {
  content: " [PDF]";
  font-size: 0.75em;
  font-weight: 700;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Contains specific value in attribute */
input[type*="search"] {
  border-radius: var(--radius-full);
  padding-left: 1rem;
}
```

### 2.2 Combinators (Child, Descendant, Grouping)
* **Requirement**: Combinators (grouping/AND, descendant selectors, child selectors).
* **Implementation**: [`static/css/main.css#L214-L271`](file:///home/meineac/pastry-shop/static/css/main.css#L214-L271)

```css
/* static/css/main.css (Lines 214-271) */
/* Child Combinator: header > nav */
header > nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1rem;
  background-color: var(--color-card-bg);
  padding: 0.75rem 1.5rem;
  border-bottom: 2px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

/* Descendant Combinator: header nav a */
header nav a {
  text-decoration: none;
  font-weight: 500;
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 0.925rem;
}

header nav a:hover {
  background-color: var(--color-bg-alt);
  color: var(--color-primary);
}

/* Grouping Combinator */
button,
input[type="submit"],
input[type="button"],
input[type="reset"] {
  cursor: pointer;
  background-color: var(--color-primary);
  color: #ffffff;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  padding: 0.55rem 1.25rem;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
}

button:hover,
input[type="submit"]:hover,
input[type="button"]:hover {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

button:active,
input[type="submit"]:active {
  background-color: var(--color-primary-active);
  transform: translateY(1px);
}
```

---

## 3. Pseudo-classes

### 3.1 Dynamic Link States (`:link`, `:visited`, `:hover`, `:active`) and `:focus`
* **Requirement**: Dynamic link states: different styles for visited, unvisited, hover, and active. Elements in `:focus`.
* **Implementation**: [`static/css/main.css#L139-L175`](file:///home/meineac/pastry-shop/static/css/main.css#L139-L175)

```css
/* static/css/main.css (Lines 139-175) */
/* Unvisited links */
a:link {
  color: var(--color-link);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
  transition: color 0.2s ease, text-decoration-color 0.2s ease;
}

/* Visited links */
a:visited {
  color: var(--color-link-visited);
}

/* Hover state */
a:hover {
  color: var(--color-primary-hover);
  text-decoration-thickness: 2px;
  cursor: pointer;
}

/* Active state */
a:active {
  color: var(--color-primary-active);
  text-decoration-thickness: 2px;
}

/* Accessible Keyboard Focus */
:focus {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

:focus-visible {
  outline: 3px solid var(--color-secondary);
  outline-offset: 3px;
}
```

### 3.2 Form Element States (`:required`, `:disabled`, `:checked`, `:out-of-range`, `:valid`, `:invalid`)
* **Requirement**: Highlight available, required, and disabled form elements, out-of-range values, and checked checkboxes/radio buttons.
* **Implementation**:
  - Global form rules in [`static/css/main.css#L396-L426`](file:///home/meineac/pastry-shop/static/css/main.css#L396-L426)
  - Detailed component form rules in [`static/css/main.css#L3106-L3173`](file:///home/meineac/pastry-shop/static/css/main.css#L3106-L3173)

```css
/* static/css/main.css (Lines 396-426) */
/* Highlight required form elements */
input:required,
select:required,
textarea:required {
  border-left: 3px solid var(--color-primary);
}

/* Highlight disabled form elements */
input:disabled,
select:disabled,
textarea:disabled,
button:disabled {
  background-color: #e9e4dc;
  color: #8c827a;
  cursor: not-allowed;
  border-color: #d0c7bd;
  opacity: 0.7;
}

/* Highlight checked checkboxes and radio buttons */
input[type="checkbox"]:checked,
input[type="radio"]:checked {
  accent-color: var(--color-primary);
}

/* Highlight out-of-range values */
input:out-of-range {
  border-color: #c53030;
  background-color: #fff5f5;
}
```

```css
/* static/css/main.css (Lines 3127-3173) */
.review-form input:required,
.review-form select:required,
.review-form textarea:required,
.checkout-form input:required,
.checkout-form select:required {
  border-left-width: 4px;
  border-left-color: var(--color-primary);
}

.review-form input:enabled,
.review-form select:enabled,
.review-form textarea:enabled,
.checkout-form input:enabled,
.checkout-form select:enabled,
.checkout-form textarea:enabled {
  background-color: #ffffff;
}

.review-form input:disabled,
.checkout-form input:disabled,
.checkout-form select:disabled {
  background-color: #e9e4dc;
  border-color: #d0c8bd;
  color: #8c827a;
  cursor: not-allowed;
  opacity: 0.7;
}

.review-form input:valid:not(:placeholder-shown),
.review-form textarea:valid:not(:placeholder-shown),
.checkout-form input[type="text"]:valid:not(:placeholder-shown) {
  border-color: #2e7d32;
}

.review-form input:invalid:focus,
.review-form textarea:invalid:focus,
.checkout-form input:invalid:focus,
.checkout-form textarea:invalid:focus {
  border-color: #c62828;
  box-shadow: 0 0 0 3px rgba(198, 40, 40, 0.2);
}

input[type="number"]:out-of-range {
  border-color: #c62828;
  background-color: #ffebee;
}
```

### 3.3 Positional Styles for Lists & Tables (`:first-child`, `:last-child`, `:nth-child`)
* **Requirement**: Positional styles for list and table elements (first, last, nth).
* **Implementation**:
  - List elements: [`static/css/main.css#L3346-L3353`](file:///home/meineac/pastry-shop/static/css/main.css#L3346-L3353)
  - Table elements: [`static/css/main.css#L4122-L4142`](file:///home/meineac/pastry-shop/static/css/main.css#L4122-L4142)

```css
/* static/css/main.css (Lines 3346-3353) */
/* Positional List Pseudo-Classes (R4.3) */
.promo-voucher-grid > li:first-child {
  border-width: 2.5px;
}

.promo-voucher-grid > li:last-child {
  position: relative;
}
```

```css
/* static/css/main.css (Lines 4122-4142) */
/* Positional pseudo-classes & zebra striping (R4.3, R15.2) */
tbody tr:nth-child(even) {
  background-color: #faf7f2;
}

tbody tr:nth-child(odd) {
  background-color: #ffffff;
}

tbody tr:hover {
  background-color: rgba(201, 138, 44, 0.09);
}

tbody tr:first-child td {
  border-top: none;
}

tbody tr:last-child td {
  border-bottom: none;
}
```

### 3.4 Language-Sensitive Quotation Marks (`:lang(en)`, `:lang(fr)`)
* **Requirement**: Display quotes based on the quotation language.
* **Implementation**:
  - Stylesheet rule: [`static/css/main.css#L1896-L1914`](file:///home/meineac/pastry-shop/static/css/main.css#L1896-L1914)
  - Template markup: [`cms/templates/cms/about.html#L42-L46`](file:///home/meineac/pastry-shop/cms/templates/cms/about.html#L42-L46)

```css
/* static/css/main.css (Lines 1896-1914) */
/* R4.5: Language-sensitive quotations */
:lang(en) > q,
q:lang(en) {
  quotes: "“" "”" "‘" "’";
}

:lang(fr) > q,
q:lang(fr) {
  quotes: "«\00a0" "\00a0»" "“" "”";
}

q::before {
  content: open-quote;
}

q::after {
  content: close-quote;
}
```

```html
<!-- cms/templates/cms/about.html (Lines 42-46) -->
    <blockquote cite="https://pastryshop.example.com/about" class="founder-quote">
        <p lang="en"><q>We believe that great pastry is not just food — it is a moment of joy, a small luxury everyone deserves.</q></p>
        <p lang="fr"><q>La pâtisserie est un art qui se déguste avec le cœur.</q></p>
        <footer>— <cite>Marie Leblanc, Founder of Pastry Shop</cite></footer>
    </blockquote>
```

---

## 4. Pseudo-elements

### 4.1 First-Letter & First-Line Paragraph Highlighting
* **Requirement**: Highlight the first letter (or line) of an article paragraph.
* **Implementation**: [`static/css/main.css#L1253-L1270`](file:///home/meineac/pastry-shop/static/css/main.css#L1253-L1270) applied to `.lead-editorial` on [`cms/templates/cms/home.html#L70`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html#L70).

```css
/* static/css/main.css (Lines 1253-1270) */
/* R3.3: First-letter and first-line styling */
.lead-editorial::first-letter {
  font-family: var(--font-serif);
  font-size: 2.85rem;
  float: left;
  line-height: 0.85;
  margin-right: 0.65rem;
  color: var(--color-primary);
  font-weight: 700;
  text-transform: uppercase;
}

.lead-editorial::first-line {
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 0.02em;
}
```

### 4.2 Contextual Beginnings and Ends (`::before`, `::after`)
* **Requirement**: Add context at the beginning and end of a text fragment (`::before`, `::after`).
* **Implementation**: [`static/css/main.css#L1287-L1310`](file:///home/meineac/pastry-shop/static/css/main.css#L1287-L1310)

```css
/* static/css/main.css (Lines 1287-1310) */
.motto-quote::before {
  content: "“";
  font-family: var(--font-serif);
  font-size: 4.5rem;
  line-height: 1;
  position: absolute;
  top: 0.25rem;
  left: 1rem;
  color: var(--color-secondary);
  opacity: 0.55;
}

.motto-quote::after {
  content: "”";
  font-family: var(--font-serif);
  font-size: 4.5rem;
  line-height: 1;
  position: absolute;
  bottom: -0.75rem;
  right: 1.5rem;
  color: var(--color-secondary);
  opacity: 0.55;
}
```

### 4.3 Unicode Markers for Unordered Lists
* **Requirement**: Style a list using Unicode characters as markers.
* **Implementation**:
  - CSS rule: [`static/css/main.css#L1884-L1895`](file:///home/meineac/pastry-shop/static/css/main.css#L1884-L1895)
  - Template application: [`cms/templates/cms/about.html#L14-L24`](file:///home/meineac/pastry-shop/cms/templates/cms/about.html#L14-L24)

```css
/* static/css/main.css (Lines 1884-1895) */
/* R3.5: Unicode character markers for unordered lists */
ul.ornate-list {
  list-style: none;
  padding-left: 0;
}

ul.ornate-list li::before {
  content: "\2726\00a0"; /* Black Four-Pointed Star Unicode marker */
  color: var(--color-secondary);
  font-size: 0.9em;
}
```

```html
<!-- cms/templates/cms/about.html (Lines 14-24) -->
<nav aria-label="Page sections" class="page-toc-nav">
    <ul class="ornate-list">
        <li><a href="#details">Company Details</a></li>
        <li><a href="#info">About Us</a></li>
        <li><a href="#history">History Timeline</a></li>
        <li><a href="#milestones">Milestones</a></li>
        <li><a href="#video">Video</a></li>
        <li><a href="#video-showcase">Behind the Scenes</a></li>
        <li><a href="#certificate">Certificate</a></li>
    </ul>
</nav>
```

### 4.4 Text Selection Styling (`::selection`)
* **Requirement**: Change styles on text selection (`::selection`).
* **Implementation**: [`static/css/main.css#L73-L82`](file:///home/meineac/pastry-shop/static/css/main.css#L73-L82)

```css
/* static/css/main.css (Lines 73-82) */
/* ::selection pseudo-element */
::selection {
  background-color: var(--color-selection-bg);
  color: var(--color-selection-text);
}

::-moz-selection {
  background-color: var(--color-selection-bg);
  color: var(--color-selection-text);
}
```

---

## 5. Typography & Text Formatting

### 5.1 Connected Fonts (Primary, Fallback, Font-Family)
* **Requirement**: Connect fonts: primary (via a font service), fallback, and `font-family`.
* **Implementation**:
  - Fonts loaded from Google Fonts in [`core/templates/core/base.html#L10-L12`](file:///home/meineac/pastry-shop/core/templates/core/base.html#L10-L12) (*Montserrat* and *Playfair Display*).
  - Custom font variables configured with robust system fallbacks in [`static/css/main.css#L29-L33`](file:///home/meineac/pastry-shop/static/css/main.css#L29-L33):

```css
/* static/css/main.css (Lines 29-33) */
  --font-serif: "Playfair Display", Georgia, "Times New Roman", serif;
  --font-sans: "Montserrat", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
```

### 5.2 Comprehensive Text Formatting
* **Requirement**: For any text fragment, configure margins and padding, headings formatted using `text-transform`, first-line indent (`text-indent`), line-height, small caps formatting (`font-variant`), word and letter spacing, word wrap, and line breaks.
* **Implementation**:
  - Headings `text-transform`, `line-height`, `letter-spacing`: [`static/css/main.css#L84-L119`](file:///home/meineac/pastry-shop/static/css/main.css#L84-L119)
  - Paragraphs & word spacing: [`static/css/main.css#L121-L125`](file:///home/meineac/pastry-shop/static/css/main.css#L121-L125)
  - Small caps formatting via `font-variant: small-caps`: [`static/css/main.css#L127-L135`](file:///home/meineac/pastry-shop/static/css/main.css#L127-L135)
  - Word wrapping & text break defaults: [`static/css/main.css#L64-L67`](file:///home/meineac/pastry-shop/static/css/main.css#L64-L67)
  - Word breaks `<wbr>` and line breaks `<br>` in quatrain: [`cms/templates/cms/home.html#L12-L20`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html#L12-L20)

```css
/* static/css/main.css (Lines 84-118) */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-serif);
  color: var(--color-primary);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  line-height: 1.25;
  letter-spacing: 0.03em;
  font-weight: 600;
}

h1 {
  font-size: 2.25rem;
  text-transform: capitalize;
  letter-spacing: 0.04em;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0.5rem;
}

h2 {
  font-size: 1.75rem;
  text-transform: capitalize;
  letter-spacing: 0.02em;
}

h3 {
  font-size: 1.35rem;
  text-transform: capitalize;
}

h4, h5, h6 {
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
```

```css
/* static/css/main.css (Lines 127-134) */
/* Small caps formatting via font-variant */
.small-caps,
abbr[title],
figcaption,
th {
  font-variant: small-caps;
  letter-spacing: 0.05em;
}
```

```html
<!-- cms/templates/cms/home.html (Lines 12-20) -->
    <blockquote cite="https://pastryshop.example.com" class="motto-quote">
        <p>
            A flake of butter, a pinch of salt,<wbr> a twist of dough,<br>
            Golden in the oven, rising warm and slow.<br>
            Each layer tells a story,<wbr> each crumb a memory,<br>
            From our kitchen to your table — with love, freshly.
        </p>
        <cite>— The Pastry Shop</cite>
    </blockquote>
```

---

## 6. Global Styles

### 6.1 Media Queries (Viewport Width & Height)
* **Requirement**: Responsive display based on viewport width and height.
* **Implementation**: [`static/css/main.css#L451-L494`](file:///home/meineac/pastry-shop/static/css/main.css#L451-L494)

```css
/* static/css/main.css (Lines 451-494) */
/* Mobile (<= 480px) */
@media (max-width: 480px) {
  html {
    font-size: 15px;
  }
  h1 {
    font-size: 1.85rem;
  }
  h2 {
    font-size: 1.45rem;
  }
  header > nav {
    padding: 0.5rem;
    gap: 0.25rem 0.5rem;
  }
  main {
    padding: 1rem 0.75rem 2rem 0.75rem;
  }
}

/* Tablet (481px to 992px) */
@media (min-width: 481px) and (max-width: 992px) {
  main {
    padding: 1.25rem 1rem 2.5rem 1rem;
  }
}

/* Desktop (>= 993px) */
@media (min-width: 993px) {
  main {
    padding: 2rem 1.5rem 3rem 1.5rem;
  }
}

/* Viewport height media query */
@media (max-height: 600px) {
  body > header {
    position: static; /* Unstick header on very short landscape viewports to conserve screen space */
  }
  main {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
  }
}
```

### 6.2 Button and Interactive Cursor Styling
* **Requirement**: Change `cursor` appearance on button hover.
* **Implementation**: [`static/css/main.css#L242-L275`](file:///home/meineac/pastry-shop/static/css/main.css#L242-L275)

```css
/* static/css/main.css (Lines 242-246, 272-275) */
button,
input[type="submit"],
input[type="button"],
input[type="reset"] {
  cursor: pointer;
  ...
}

summary,
select {
  cursor: pointer;
}
```

### 6.3 Site Background Configuration
* **Requirement**: Configure the site background.
* **Implementation**: [`static/css/main.css#L10-L12`](file:///home/meineac/pastry-shop/static/css/main.css#L10-L12) and [`#L56-L61`](file:///home/meineac/pastry-shop/static/css/main.css#L56-L61)

```css
/* static/css/main.css (Lines 56-61) */
body {
  font-family: var(--font-sans);
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text);
  background-color: var(--color-bg);
}
```

---

## 7. Specific Page Requirements

### 7.1 Catalog: CSS Grid Layout
* **Requirement**: Use **CSS Grid Layout** for goods/services catalog.
* **Implementation**: [`static/css/main.css#L761-L770`](file:///home/meineac/pastry-shop/static/css/main.css#L761-L770) applied to `.product-grid` in [`catalog/templates/catalog/product_list.html`](file:///home/meineac/pastry-shop/catalog/templates/catalog/product_list.html):

```css
/* static/css/main.css (Lines 761-770) */
/* CSS Grid Catalog */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.75rem;
  list-style: none;
  padding: 0;
  margin: 0;
}
```

### 7.2 Main Page
* **Requirement**:
  - Circular blocks for partner companies list; configure width, color, type, and shadow.
  - Configure font and kerning for company names.
  - Use `position` to display info about the latest article.
  - Fixed navigation area during scrolling.
* **Implementation**:
  - Sticky/Fixed Navigation: [`static/css/main.css#L280-L287`](file:///home/meineac/pastry-shop/static/css/main.css#L280-L287)
  - Circular Partner Blocks: [`static/css/main.css#L1518-L1537`](file:///home/meineac/pastry-shop/static/css/main.css#L1518-L1537)
  - Partner Typography & Kerning: [`static/css/main.css#L1566-L1578`](file:///home/meineac/pastry-shop/static/css/main.css#L1566-L1578)
  - Latest Article Positioning & Ribbon: [`static/css/main.css#L1588-L1624`](file:///home/meineac/pastry-shop/static/css/main.css#L1588-L1624)

```css
/* static/css/main.css (Lines 280-287) */
/* R6.4: Fixed/Sticky Navigation */
body > header {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
}
```

```css
/* static/css/main.css (Lines 1518-1536) */
.partner-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 3px solid var(--color-secondary);
  box-shadow: 0 6px 16px rgba(92, 61, 46, 0.14);
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.partner-link:hover .partner-circle {
  transform: scale(1.08);
  box-shadow: 0 10px 22px rgba(139, 58, 43, 0.25);
  border-color: var(--color-primary);
}
```

```css
/* static/css/main.css (Lines 1566-1578) */
/* R6.2: Partner company names font and kerning */
.partner-name {
  display: block;
  margin-top: 0.75rem;
  font-family: var(--font-serif);
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.08em; /* Configured kerning */
  text-transform: uppercase;
  color: var(--color-text);
  text-align: center;
  transition: color 0.2s ease;
}
```

```css
/* static/css/main.css (Lines 1588-1624) */
.latest-news-card {
  position: relative; /* Relative positioning container */
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.75rem;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  align-items: center;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}

/* Absolute positioned ribbon badge */
.news-ribbon-badge {
  position: absolute;
  top: 18px;
  right: -34px;
  background-color: var(--color-primary);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.35rem 2.75rem;
  transform: rotate(45deg);
  box-shadow: 0 2px 6px rgba(44, 34, 30, 0.25);
  z-index: 3;
}
```

### 7.3 About Company
* **Requirement**:
  - Apply `transform` to the logo.
  - Certificate: `border-image` from graphic file with vendor prefixes, `background-image`, gradients, `z-index`, font styling, and text alignment.
  - History timeline as a list, highlight requisites via font, custom styling for video/audio.
* **Implementation**:
  - Logo Transform: [`static/css/main.css#L1935-L1956`](file:///home/meineac/pastry-shop/static/css/main.css#L1935-L1956)
  - Certificate Ticket & Border Image with vendor prefixes (`-webkit-`, `-moz-`, `-o-`), `radial-gradient`, `z-index`: [`static/css/main.css#L1958-L2041`](file:///home/meineac/pastry-shop/static/css/main.css#L1958-L2041)
  - History Timeline: [`static/css/main.css#L2056-L2091`](file:///home/meineac/pastry-shop/static/css/main.css#L2056-L2091)
  - Video and Audio Players: [`static/css/main.css#L2155-L2183`](file:///home/meineac/pastry-shop/static/css/main.css#L2155-L2183)

```css
/* static/css/main.css (Lines 1935-1956) */
/* R7.1: Company Logo Transform Effect */
.about-logo-figure {
  text-align: center;
  margin: 2.5rem auto;
  perspective: 1000px;
}

.about-logo-img {
  width: 250px;
  height: auto;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  border: 3px solid var(--color-border);
  transform: rotate(-2deg) scale(0.98);
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease, border-color 0.4s ease;
}

.about-logo-img:hover {
  transform: rotate(0deg) scale(1.06);
  box-shadow: 0 14px 30px rgba(139, 58, 43, 0.25);
  border-color: var(--color-secondary);
}
```

```css
/* static/css/main.css (Lines 1963-2026) */
.certificate-ticket-container {
  position: relative;
  max-width: 720px;
  margin: 2rem auto;
  padding: 2.5rem 2.25rem;
  text-align: center;
  background: radial-gradient(circle at center, #ffffff 0%, #faf3e8 70%, #f4e8d3 100%);
  border: 24px solid transparent;
  -webkit-border-image: url("/static/images/certificate_border.svg") 30 round;
  -moz-border-image: url("/static/images/certificate_border.svg") 30 round;
  -o-border-image: url("/static/images/certificate_border.svg") 30 round;
  border-image: url("/static/images/certificate_border.svg") 30 round;
  box-shadow: 0 10px 30px rgba(92, 61, 46, 0.16);
  overflow: hidden;
  z-index: 1;
}

.certificate-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  margin-top: -100px;
  margin-left: -100px;
  background: url("/static/images/certificate_watermark.svg") no-repeat center center;
  background-size: contain;
  opacity: 0.22;
  pointer-events: none;
  z-index: 2;
}

.certificate-inner {
  position: relative;
  z-index: 3;
}

.certificate-text,
.certificate-section pre {
  font-family: var(--font-serif);
  font-size: 1.15rem;
  line-height: 1.8;
  color: var(--color-text);
  white-space: pre-wrap;
  background: transparent;
  border: none;
  padding: 0;
  margin: 1.25rem 0;
  text-align: center;
  letter-spacing: 0.02em;
}
```

```css
/* static/css/main.css (Lines 2056-2091) */
/* History Timeline */
.history-timeline {
  position: relative;
  border-left: 3px solid var(--color-secondary);
  margin-left: 1rem;
  padding-left: 1.75rem;
}

.history-timeline dt {
  position: relative;
  font-family: var(--font-serif);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-top: 1.25rem;
}

.history-timeline dt::before {
  content: "";
  position: absolute;
  left: -2.25rem;
  top: 0.35rem;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: var(--color-secondary);
  border: 3px solid #ffffff;
  box-shadow: 0 0 0 2px var(--color-secondary);
}
```

### 7.4 News
* **Requirement**:
  - List of 7 thematic articles with a title, short description, image, and "Read more" button.
  - `overflow` and `text-overflow: ellipsis` for truncated descriptions.
  - Multi-column layout for article text on detail page.
* **Implementation**:
  - Template 7-item slice and structure: [`cms/templates/cms/news_list.html#L38-L74`](file:///home/meineac/pastry-shop/cms/templates/cms/news_list.html#L38-L74)
  - Ellipsis Truncation: [`static/css/main.css#L2310-L2323`](file:///home/meineac/pastry-shop/static/css/main.css#L2310-L2323)
  - Multi-column Layout (`column-count: 2`, `column-gap`, `column-rule`): [`static/css/main.css#L2395-L2409`](file:///home/meineac/pastry-shop/static/css/main.css#L2395-L2409)

```html
<!-- cms/templates/cms/news_list.html (Lines 38-40, 71-74) -->
<ul class="news-grid">
{% for item in news|slice:":7" %}
    <li class="news-card" itemscope itemtype="https://schema.org/NewsArticle">
        ...
        <p itemprop="description" class="news-card-desc">{{ item.short_summary }}</p>
        <div class="news-card-actions">
            <a href="{% url 'cms:news_detail' pk=item.id %}" class="btn-read-more">Read More &rarr;</a>
        </div>
```

```css
/* static/css/main.css (Lines 2310-2323) */
/* R8.2: Truncated description with text-overflow: ellipsis */
.news-card-desc {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 1.25rem;
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
```

```css
/* static/css/main.css (Lines 2395-2409) */
/* Multi-column layout */
.news-article-columns {
  column-count: 2;
  column-gap: 3rem;
  column-rule: 1px solid var(--color-border);
  line-height: 1.8;
  text-align: justify;
  margin: 2rem 0;
  font-size: 1.05rem;
}

.news-article-columns p {
  margin-top: 0;
}
```

### 7.5 Glossary (Q&A)
* **Requirement**: Q&A list with date added; clicking reveals a detailed answer with custom styling.
* **Implementation**:
  - Template structure using semantic `<details>` and `<summary>`: [`cms/templates/cms/qna_list.html#L38-L65`](file:///home/meineac/pastry-shop/cms/templates/cms/qna_list.html#L38-L65)
  - Accordion styling with rotating disclosure marker: [`static/css/main.css#L2410-L2478`](file:///home/meineac/pastry-shop/static/css/main.css#L2410-L2478)

```css
/* static/css/main.css (Lines 2456-2473) */
.qna-summary::after {
  content: "▾";
  font-size: 1.25rem;
  color: var(--color-secondary);
  transition: transform 0.25s ease;
  margin-left: 1rem;
  flex-shrink: 0;
}

.qna-item details[open] .qna-summary::after {
  transform: rotate(180deg);
}

.qna-item details[open] .qna-summary {
  border-bottom: 1px solid var(--color-border);
  background-color: #faf4ec;
}
```

### 7.6 Contacts
* **Requirement**: Employee photos, job descriptions, phone, email. Use **Flexbox** for layout.
* **Implementation**:
  - Stylesheet: [`static/css/main.css#L2616-L2651`](file:///home/meineac/pastry-shop/static/css/main.css#L2616-L2651)
  - Template markup: [`cms/templates/cms/contacts.html#L38-L69`](file:///home/meineac/pastry-shop/cms/templates/cms/contacts.html#L38-L69)

```css
/* static/css/main.css (Lines 2616-2644) */
/* R9.1: Team members Flexbox layout */
.team-flex-container {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  list-style: none;
  padding: 0;
  margin: 2rem 0;
}

.employee-card {
  flex: 1 1 calc(33.333% - 2rem);
  min-width: 260px;
  max-width: 380px;
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
```

### 7.7 Privacy Policy
* **Requirement**: Custom style matching the site theme.
* **Implementation**: [`static/css/main.css#L3354-L3520`](file:///home/meineac/pastry-shop/static/css/main.css#L3354-L3520) applied to [`cms/templates/cms/privacy_policy.html`](file:///home/meineac/pastry-shop/cms/templates/cms/privacy_policy.html) featuring pastry-shop warm cream background, subtle borders, jump links navigation, and definition lists `<dl>/<dt>/<dd>`.

### 7.8 Vacancies
* **Requirement**: List of vacancies with descriptions using floats (`float`, `clear`).
* **Implementation**:
  - Stylesheet: [`static/css/main.css#L2716-L2812`](file:///home/meineac/pastry-shop/static/css/main.css#L2716-L2812)
  - Template markup: [`cms/templates/cms/vacancies_list.html#L38-L78`](file:///home/meineac/pastry-shop/cms/templates/cms/vacancies_list.html#L38-L78)

```css
/* static/css/main.css (Lines 2716-2811) */
/* Float styling */
.vacancy-header-float {
  float: left;
  width: calc(100% - 250px);
  margin-bottom: 0.5rem;
}

.vacancy-meta-badge-float {
  float: right;
  width: 220px;
  text-align: right;
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.vacancy-desc-float {
  float: left;
  width: calc(100% - 250px);
  clear: left;
  line-height: 1.7;
  color: var(--color-text);
  margin: 0.75rem 0 1.25rem 0;
}

.vacancy-apply-float {
  clear: both; /* Clearfix for both floats */
  padding-top: 1rem;
  border-top: 1px dashed var(--color-border);
}

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
```

### 7.9 Reviews
* **Requirement**: Use keywords corresponding to the component type for form font settings, applying pseudo-classes.
* **Implementation**:
  - System font keywords (`caption`, `menu`, `message-box`, `small-caption`, `status-bar`): [`static/css/main.css#L3002-L3070`](file:///home/meineac/pastry-shop/static/css/main.css#L3002-L3070)
  - Form state pseudo-classes: [`static/css/main.css#L3106-L3173`](file:///home/meineac/pastry-shop/static/css/main.css#L3106-L3173)

```css
/* static/css/main.css (Lines 3002-3069) */
/* System Font Keywords (R12.1) */
.review-form label {
  font: caption; /* system font keyword */
  display: block;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.review-form select {
  font: menu; /* system font keyword */
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  ...
}

.review-form textarea {
  font: message-box; /* system font keyword */
  width: 100%;
  padding: 0.85rem 1rem;
  ...
}

.review-form input[type="text"] {
  font: menu; /* system font keyword */
  width: 100%;
  ...
}

.review-form .helptext {
  font: small-caption; /* system font keyword */
  display: block;
  color: var(--color-text-muted);
  ...
}

.form-status-indicator {
  font: status-bar; /* system font keyword */
  display: block;
  color: var(--color-text-muted);
  ...
}
```

### 7.10 Promo Codes & Coupons
* **Requirement**: Lists of active and archived promo codes. Style the lists.
* **Implementation**:
  - Stylesheet: [`static/css/main.css#L3206-L3334`](file:///home/meineac/pastry-shop/static/css/main.css#L3206-L3334)
  - Template structure: [`cms/templates/cms/promo_codes.html#L13-L80`](file:///home/meineac/pastry-shop/cms/templates/cms/promo_codes.html#L13-L80)
  - Active vouchers are styled as vibrant dashed ticket cards with discount badges; archived vouchers are formatted with muted colors, struck-through badges (`<del>`), and grayscale filters.

```css
/* static/css/main.css (Lines 3216-3228) */
/* Active Voucher Styling (R13.1): Vibrant ticket coupon */
.active-voucher {
  background: linear-gradient(135deg, #ffffff 0%, #fffcf7 60%, #fef5e7 100%);
  border: 2px dashed var(--color-secondary);
  box-shadow: 0 4px 15px rgba(201, 138, 44, 0.16);
}

.active-voucher:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(201, 138, 44, 0.25);
  border-color: var(--color-primary);
}
```

```css
/* static/css/main.css (Lines 3299-3310) */
/* Archived Voucher Styling (R13.1): Muted / struck-through expired */
.archived-voucher {
  background-color: #f3efe9;
  border: 2px dashed #c8bfb4;
  opacity: 0.78;
  filter: grayscale(0.2);
}
```

---

## 8. Tables

* **Requirement**:
  - Remove double borders between cells (`border-collapse: collapse`).
  - Change the background of empty cells (`empty-cells: show`, `td:empty`).
  - Place table caption above table (`caption-side: top`).
  - Apply horizontal and vertical alignment for cell content and adjust table positioning on the page.
  - Style specific rows and columns (`:nth-child`, `:hover`).
* **Implementation**: [`static/css/main.css#L4074-L4155`](file:///home/meineac/pastry-shop/static/css/main.css#L4074-L4155)

```css
/* static/css/main.css (Lines 4074-4155) */
table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse; /* R15.1: removes double borders */
  empty-cells: show; /* R15.1: empty cells shown */
  caption-side: top; /* R15.1: caption placed above table */
  margin: 1.75rem auto 2.25rem auto; /* R15.2: properly positioned on page */
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

caption {
  font-family: var(--font-serif);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-primary);
  text-align: left;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  letter-spacing: 0.03em;
}

thead th {
  background-color: var(--color-primary);
  color: #ffffff;
  font-family: var(--font-serif);
  font-size: 0.92rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.9rem 1.1rem;
  border-bottom: 2px solid #6b2b1f;
  text-align: left; /* R15.2: horizontal alignment */
  vertical-align: middle; /* R15.2: vertical alignment */
}

tbody td {
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left; /* R15.2: horizontal alignment */
  vertical-align: middle; /* R15.2: vertical alignment */
  color: var(--color-text);
  font-size: 0.92rem;
}

/* Positional pseudo-classes & zebra striping (R4.3, R15.2) */
tbody tr:nth-child(even) {
  background-color: #faf7f2;
}

tbody tr:nth-child(odd) {
  background-color: #ffffff;
}

tbody tr:hover {
  background-color: rgba(201, 138, 44, 0.09);
}

tbody tr:first-child td {
  border-top: none;
}

tbody tr:last-child td {
  border-bottom: none;
}

/* Empty cell styling (R15.1) */
td:empty {
  background-color: #f5f1eb;
  position: relative;
}

td:empty::after {
  content: "—";
  color: var(--color-text-muted);
  display: block;
  text-align: center;
}
```

---

## 9. Animations & Preloader (Individual Assignment: Pastry Shop)

### 9.1 Preloader: Infinity Symbol
* **Assignment Variant**: Preloader matching assigned variant: **Infinity symbol** (a colored line moving along the shape) placed statically at the bottom of the page without JS scripts.
* **Implementation**:
  - Stylesheet keyframe animation tracing stroke-dashoffset: [`static/css/main.css#L1673-L1724`](file:///home/meineac/pastry-shop/static/css/main.css#L1673-L1724)
  - Bottom-of-page HTML placement: [`cms/templates/cms/home.html#L267-L276`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html#L267-L276)

```css
/* static/css/main.css (Lines 1693-1716) */
.preloader-track {
  fill: none;
  stroke: #eedfcb;
  stroke-width: 4.5;
}

.preloader-trace {
  fill: none;
  stroke: var(--color-primary);
  stroke-width: 4.5;
  stroke-linecap: round;
  stroke-dasharray: 45 155;
  stroke-dashoffset: 200;
  animation: trace-infinity-contour 2.5s linear infinite;
}

@keyframes trace-infinity-contour {
  0% {
    stroke-dashoffset: 200;
  }
  100% {
    stroke-dashoffset: 0;
  }
}
```

```html
<!-- cms/templates/cms/home.html (Lines 267-276) -->
{% comment %}Main Page Preloader (R6.5){% endcomment %}
<section class="home-preloader-section" aria-label="Page preloader">
    <div class="preloader-container">
        <svg class="preloader-infinity" viewBox="0 0 100 50" width="80" height="40" role="img" aria-label="Infinity Preloader">
            <path class="preloader-track" d="M 25,25 C 25,12 38,12 50,25 C 62,38 75,38 75,25 C 75,12 62,12 50,25 C 38,38 25,38 25,25 Z" />
            <path class="preloader-trace" d="M 25,25 C 25,12 38,12 50,25 C 62,38 75,38 75,25 C 75,12 62,12 50,25 C 38,38 25,38 25,25 Z" />
        </svg>
        <span class="preloader-text">Freshly baking new treats...</span>
    </div>
</section>
```

### 9.2 Main Page Animation: Pastries Swirling into Smiling Cloud
* **Assignment Variant**: Pastries appear on screen, swirl, and smoothly descend into a cloud floating below. The cloud smiles and changes color. The company name appears and remains on screen.
* **Implementation**:
  - Stylesheet animations: [`static/css/main.css#L1311-L1486`](file:///home/meineac/pastry-shop/static/css/main.css#L1311-L1486)
  - Showcase markup: [`cms/templates/cms/home.html#L23-L47`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html#L23-L47)

```html
<!-- cms/templates/cms/home.html (Lines 23-47) -->
<section class="pastry-animation-showcase" aria-label="Artisanal Bakery Showcase">
    <div class="animation-stage">
        <!-- Swirling Pastries -->
        <span class="animated-pastry pastry-1" aria-hidden="true">🥐</span>
        <span class="animated-pastry pastry-2" aria-hidden="true">🧁</span>
        <span class="animated-pastry pastry-3" aria-hidden="true">🥧</span>
        <span class="animated-pastry pastry-4" aria-hidden="true">🍪</span>

        <!-- Smiling, Color-Changing Cloud -->
        <div class="animated-cloud" aria-hidden="true">
            <div class="cloud-face">
                <span class="cloud-eye eye-left"></span>
                <span class="cloud-eye eye-right"></span>
                <span class="cloud-smile"></span>
            </div>
        </div>

        <!-- Persistent Company Name -->
        <div class="animated-brand-banner">
            <span class="animated-brand-title">Pastry Shop</span>
            <span class="animated-brand-subtitle">Baked with Joy &amp; Tradition</span>
        </div>
    </div>
</section>
```

```css
/* static/css/main.css (Lines 1349-1370) — Swirl and Descend */
@keyframes swirl-and-descend {
  0% {
    opacity: 0;
    transform: translate(-100px, -20px) rotate(-180deg) scale(0.4);
  }
  15% {
    opacity: 1;
    transform: translate(-50px, 15px) rotate(-45deg) scale(1.1);
  }
  45% {
    opacity: 1;
    transform: translate(60px, 45px) rotate(180deg) scale(0.95);
  }
  75% {
    opacity: 0.85;
    transform: translate(-10px, 85px) rotate(320deg) scale(0.7);
  }
  90%, 100% {
    opacity: 0;
    transform: translate(0px, 120px) rotate(420deg) scale(0.1);
  }
}
```

```css
/* static/css/main.css (Lines 1411-1422) — Cloud Smiling & Cycling Color */
@keyframes cloud-color-cycle {
  0% { background-color: #ffffff; }
  25% { background-color: #ffe6ea; } /* gentle strawberry blush */
  50% { background-color: #fff4d4; } /* warm honey pastry */
  75% { background-color: #e5f4e3; } /* subtle pistachio */
  100% { background-color: #ffffff; }
}

@keyframes cloud-gentle-hover {
  0% { transform: translateY(0); }
  100% { transform: translateY(-8px); }
}
```

```css
/* static/css/main.css (Lines 1461-1485) — Persistent Company Name */
.animated-brand-banner {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
}

.animated-brand-title {
  display: block;
  font-family: var(--font-serif);
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 0.05em;
}

.animated-brand-subtitle {
  display: block;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-secondary);
  font-weight: 600;
}
```

---

## 10. Summary Verification Table

| Requirement Group | Specific Feature | File Reference | Line Numbers |
| :--- | :--- | :--- | :--- |
| **Constraints** | Zero framework/Bootstrap CDN | [`core/templates/core/base.html`](file:///home/meineac/pastry-shop/core/templates/core/base.html) | L10–L15 |
| **Constraints** | Ornate ticket certificate | [`cms/templates/cms/about.html`](file:///home/meineac/pastry-shop/cms/templates/cms/about.html) | L211–L227 |
| **Selectors** | Attribute selectors (`^=`, `$=`, `*=`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L180–L212 |
| **Selectors** | Combinators (child, descendant, grouping) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L214–L271 |
| **Pseudo-classes** | Link states (`:link`, `:visited`, `:hover`, `:active`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L139–L165 |
| **Pseudo-classes** | Focus styles (`:focus`, `:focus-visible`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L166–L175 |
| **Pseudo-classes** | Form element state pseudo-classes | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L396–L426, L3106–L3173 |
| **Pseudo-classes** | Positional pseudo-classes (`:first-child`, `:last-child`, `:nth-child`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L3346–L3353, L4122–L4142 |
| **Pseudo-classes** | Language-sensitive quotation marks (`:lang(en)`, `:lang(fr)`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1896–L1914 |
| **Pseudo-elements** | Drop caps & first line (`::first-letter`, `::first-line`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1253–L1270 |
| **Pseudo-elements** | Contextual borders (`::before`, `::after`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1287–L1310 |
| **Pseudo-elements** | Unicode list markers (`.ornate-list li::before`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1884–L1895 |
| **Pseudo-elements** | Text selection styling (`::selection`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L73–L82 |
| **Typography** | Font connecting (Google Fonts + fallbacks) | [`core/templates/core/base.html`](file:///home/meineac/pastry-shop/core/templates/core/base.html) & [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L10–L12, L29–L33 |
| **Typography** | Headings `text-transform`, `line-height`, `letter-spacing` | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L84–L119 |
| **Typography** | Small caps formatting (`font-variant: small-caps`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L127–L135 |
| **Typography** | Word wrap, `<wbr>`, `<br>` quatrain | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/home.html`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html) | L64–L67, L12–L20 |
| **Global Styles** | Responsive media queries (width & height) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L451–L494 |
| **Global Styles** | Cursor styling on buttons & interactive elements | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L242–L275 |
| **Global Styles** | Site background color styling | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L10–L12, L56–L61 |
| **Catalog** | CSS Grid Layout (`product-grid`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L761–L770 |
| **Main Page** | Circular partner blocks with shadow/hover | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1518–L1537 |
| **Main Page** | Partner company font & kerning | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1566–L1578 |
| **Main Page** | Relative latest news card & ribbon badge | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1588–L1624 |
| **Main Page** | Fixed/sticky navigation during scrolling | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L280–L287 |
| **About Company** | Logo CSS transform (`rotate`, `scale`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1935–L1956 |
| **About Company** | Certificate `border-image`, vendor prefixes, radial gradient | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L1958–L2041 |
| **About Company** | History timeline with styled date markers | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L2056–L2091 |
| **About Company** | Video & audio media containers | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L2155–L2183 |
| **News** | Exactly 7 articles with image, title, read more | [`cms/templates/cms/news_list.html`](file:///home/meineac/pastry-shop/cms/templates/cms/news_list.html) | L38–L86 |
| **News** | Ellipsis clipping (`text-overflow: ellipsis`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L2310–L2323 |
| **News** | Multi-column layout on article detail | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L2395–L2409 |
| **Glossary (Q&A)** | `<details>` / `<summary>` accordion with animated disclosure indicator | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/qna_list.html`](file:///home/meineac/pastry-shop/cms/templates/cms/qna_list.html) | L2410–L2500, L40–L65 |
| **Contacts** | Team members Flexbox layout (`display: flex; flex-wrap: wrap`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/contacts.html`](file:///home/meineac/pastry-shop/cms/templates/cms/contacts.html) | L2616–L2651, L40–L68 |
| **Privacy Policy** | Pastry-shop themed document card & jump navigation | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/privacy_policy.html`](file:///home/meineac/pastry-shop/cms/templates/cms/privacy_policy.html) | L3354–L3520, L5–L160 |
| **Vacancies** | Float layout (`float: left`, `float: right`, `clear: both`, `.clearfix`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/vacancies_list.html`](file:///home/meineac/pastry-shop/cms/templates/cms/vacancies_list.html) | L2716–L2812, L40–L74 |
| **Reviews** | System font keywords (`caption`, `menu`, `message-box`, `small-caption`, `status-bar`) | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L3002–L3070 |
| **Promo Codes** | Active & archived voucher card styling | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/promo_codes.html`](file:///home/meineac/pastry-shop/cms/templates/cms/promo_codes.html) | L3206–L3334, L15–L80 |
| **Tables** | `border-collapse`, `empty-cells`, `caption-side: top`, alignment, hover | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) | L4074–L4155 |
| **Animations** | Main page swirling pastries into smiling, color-changing cloud + brand banner | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/home.html`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html) | L1311–L1486, L23–L47 |
| **Preloader** | Infinity symbol moving along contour placed at bottom of page | [`static/css/main.css`](file:///home/meineac/pastry-shop/static/css/main.css) & [`cms/templates/cms/home.html`](file:///home/meineac/pastry-shop/cms/templates/cms/home.html) | L1673–L1724, L267–L276 |