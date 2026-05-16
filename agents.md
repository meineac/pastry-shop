# Agent Instructions — Pastry Shop Django Project

## Project Overview
This is a Django-based web application for a Pastry Shop. It is a full-stack project with authentication, a product catalog, a cart/checkout system, a CMS, statistics,
and third-party API integrations (IPinfo and OpenWeather).

## Critical Architecture Rules — READ BEFORE WRITING ANY CODE

### 0. Form validation must be on both the server side and the client side.

### 1. Views: ONLY Function-Based Views (FBV)
- You are FORBIDDEN from using Class-Based Views (CBV).
- No: CreateView, UpdateView, ListView, DetailView, LoginView, TemplateView, or any CBV.

### 2. URL Routing: ONLY `re_path()` with Regular Expressions
- You are FORBIDDEN from using `path()` with angle brackets (`<int:pk>`, `<str:slug>`).
- ALL URL patterns must use `re_path()` with explicit regex.

### 3. Database
- Development: SQLite (default Django setting).
- Production/Docker: PostgreSQL (via environment variable DATABASE_URL).

### 4. No JavaScript
- Zero client-side JavaScript is permitted anywhere in the project.

### 5. Abstract Base Model
- ALL core domain entities must inherit from `TimestampedModel`.
- Simple lookup/tag models (e.g., NewsTag, VacancyTag) use plain `models.Model`.
- `TimestampedModel` provides `created_at` and `updated_at`.

### 6. Phone Number Format
- All phone numbers must be stored and displayed as: `+375 (29) XXX-XX-XX`
- Enforce this format with a RegexValidator on the model field.

### 7. Age Restriction
- Clients (CustomerProfile) and Staff (StaffProfile) must be 18 or older (calculate age based on birthday).

### 8. Date Display Format
- ALL dates must use the format `DD/MM/YYYY` for display.

### 9. Logging
- Use Django's logging framework throughout the project.
- Log levels must be configurable via `settings.py` (read from environment variable `LOG_LEVEL`, default `DEBUG`).

### 10. Testing
- Target: 80%+ test coverage.
