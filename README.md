# داروخانه آرمان — Arman Pharmacy Store

Full-stack online pharmacy store: Django 5 + PostgreSQL backend, server-rendered
SEO-first frontend, RTL Persian UI with progressive-enhancement animations.

## Stack

- **Backend:** Django 5.2, PostgreSQL, Redis (cache + rate limiting)
- **Payments:** ZarinPal (sandbox-ready via `ZARINPAL_SANDBOX=True`)
- **Frontend:** Server-rendered Django templates, self-hosted Vazirmatn font,
  vanilla CSS/JS (no frontend build step, no client-side framework — every
  page is fully rendered HTML on first response)
- **Static files:** WhiteNoise (compressed + manifest-hashed in production)

## Why this architecture (SEO + animation, together)

Every page is fully rendered server-side — no content ever depends on
client-side JavaScript running to become visible or indexable. Animations
(scroll-reveal, hover states, micro-interactions) are a layer strictly on
top of that:

- `.reveal` elements start at `opacity:0` but are always present, complete,
  and crawlable in the raw HTML.
- If JavaScript is disabled/blocked, `.no-js .reveal` (set before JS loads,
  removed by `main.js` on the first tick) forces full visibility immediately.
- If JavaScript runs but a crawler never scrolls the page (a real behavior
  of some renderers), a 2.5s fallback timer force-reveals everything anyway
  — see `initReveal()` in `static/js/main.js`.
- `prefers-reduced-motion: reduce` disables all animation duration globally.
- All cart/quantity/remove actions are real `<form method="post">` elements;
  JS intercepts `submit` for a faster AJAX experience but falls back to a
  normal form post if `fetch` fails.

## Backend hardening checklist

- Custom phone-number-based `User` model, rate-limited login/register/contact
  forms (`django-ratelimit`)
- Strict Content-Security-Policy (`django-csp`) — `script-src` allows only
  `'self'` + a per-request nonce (used for JSON-LD `<script>` blocks)
- HSTS, secure cookies, `X-Frame-Options: DENY`, `X-Content-Type-Options`,
  `Referrer-Policy`, `Permissions-Policy` (all in `config/settings/prod.py` /
  `base.py`)
- Configurable admin URL (`DJANGO_ADMIN_URL` env var) instead of `/admin/`
- Checkout uses `select_for_update()` inside an atomic transaction to
  prevent overselling under concurrent checkouts (see
  `apps/orders/views.py::checkout` and its regression test)
- File upload size limits; prescription uploads are plain `ImageField`s
  validated by Django's upload handlers
- Structured logging (rotating file handlers, separate `security.log`)
- The custom 500 page renders without going through context processors, so
  a database outage can't also break the error page itself

## SEO checklist

- `sitemap.xml` (products, categories, static pages) + `robots.txt`,
  auto-generated from the database
- Every page sets a real `<title>`, meta description, canonical URL,
  Open Graph + Twitter Card tags
- JSON-LD structured data: `Organization` (sitewide), `Product` + `Offer`
  (product pages, price converted to Rial/IRR per schema.org), `BreadcrumbList`
- Persian-slug URLs (`/products/<uslug>/`) via a custom unicode-slug path
  converter — no ASCII transliteration of product names
- Thin/duplicate pages (search results, cart, checkout, account pages) are
  marked `noindex,follow`
- Self-hosted woff2 fonts with `font-display: swap` (no external font CDN
  round-trip blocking render)
- Images use `loading="lazy"` + explicit `width`/`height` to avoid layout
  shift (CLS)

## Local setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env   # then edit DJANGO_SECRET_KEY, DATABASE_URL, etc.

createdb arman_pharmacy   # or via psql, matching DATABASE_URL

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data   # optional: sample categories/products
python manage.py runserver
```

Run tests: `pytest`

## Production

Set `DJANGO_SETTINGS_MODULE=config.settings.prod` and fill in the production
`.env` (real `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`,
`REDIS_URL`, `ZARINPAL_MERCHANT_ID` with `ZARINPAL_SANDBOX=False`, SMTP
settings). Serve with `gunicorn config.wsgi:application`, behind a reverse
proxy that terminates TLS and sets `X-Forwarded-Proto`. Run
`python manage.py collectstatic` as part of your deploy step.
