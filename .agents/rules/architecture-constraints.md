# Architecture Constraints — MUST NOT VIOLATE

These are non-negotiable rules for the Pastry Shop Django project. Any code suggestion or edit that violates one of these must not be applied.

## 1. Views: Function-Based Views (FBV) only
Forbidden: CreateView, UpdateView, ListView, DetailView, LoginView, TemplateView, or any Class-Based View. All logic — including authentication and registration — is implemented via FBV.

## 2. URL routing: `re_path()` only
Forbidden: `path()` with angle brackets (e.g. `<int:pk>`, `<str:slug>`). All URL patterns use `re_path()` with explicit regex.

## 3. No JavaScript
Zero client-side JavaScript anywhere in the project — no `<script>` tags, no inline event handlers (`onclick=`, etc.), no JS form validation. Client-side validation is done with HTML5 attributes only (`required`, `pattern`, `min`, `max`).

## 4. Abstract base model
All core domain entities inherit from `TimestampedModel` (abstract base providing `created_at` / `updated_at`). Simple lookup/tag models (e.g. NewsTag, VacancyTag) use plain `models.Model` instead.

## 5. Phone number format
Stored and displayed as: `+375 (29) XXX-XX-XX`. Enforced via `RegexValidator` on the model field.

## 6. Age restriction
`CustomerProfile` and `StaffProfile` require the person to be 18+, calculated from date of birth (model `clean()` or form validation).

## 7. Date display format
All dates are displayed as `DD/MM/YYYY`. In templates use `|date:"d/m/Y"` (or the project's equivalent filter).

## 8. Server-side validation is mandatory
Every form must validate on the server side regardless of any HTML5 client-side validation present.