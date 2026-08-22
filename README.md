# Chapter & Verse — Backend

Django REST Framework backend for a bookstore ecommerce platform. Includes JWT authentication, eSewa payments, catalog, cart, checkout, reviews, discounts, and staff analytics.

**Frontend:** [`chapter-and-verse-frontend`](https://github.com/bunnyhboy/pagehaus-frontend) — Next.js, TypeScript, Tailwind

## Stack

|           |                                       |
| --------- | ------------------------------------- |
| Framework | Django + Django REST Framework        |
| Auth      | JWT (`djangorestframework-simplejwt`) |
| Database  | SQLite (development)                  |
| Payments  | eSewa ePay v2                         |
| Filtering | `django-filter`                       |

## App Structure

| App         | Responsibility                                       |
| ----------- | ---------------------------------------------------- |
| `account`   | Registration, email verification, JWT auth, profiles |
| `books`     | Catalog, search, filtering, sorting                  |
| `cart`      | User carts and cart items                            |
| `discount`  | Coupons, limits, expiry                              |
| `orders`    | Orders, price snapshots, stock, cancellation         |
| `payment`   | eSewa payment initiation and verification            |
| `reviews`   | Verified-purchase reviews and ratings                |
| `dashboard` | Read-only staff analytics                            |
| `library`   | Reserved for future ebook features                   |

## Key Decisions

* **Price snapshotting:** `OrderItem` stores the book title and price at purchase time, preserving historical order accuracy.
* **Concurrency-safe stock:** Checkout uses `select_for_update()` inside a transaction to prevent overselling during concurrent purchases.
* **Verified reviews:** Reviews can require a delivered purchase, with verification performed server-side.
* **Secure payments:** eSewa HMAC signing, response verification, and server-to-server status checks are handled entirely by the backend.
* **Model-free dashboard:** Analytics use Django ORM aggregations instead of duplicating data.
* **UUID primary keys:** Prevent exposing record counts and creation order through URLs.

## API Conventions

* Class-based DRF views (`APIView`/generics)
* Serializer validation for fast feedback
* Transaction-level validation for concurrency safety
* No pagination configured yet

## Known Limitations

* Automated tests are not implemented yet
* List endpoints are not paginated
* `library` is not implemented
* Media files use local storage in development
* SQLite is currently used for development
