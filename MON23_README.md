# Mon 23 – Ramya: cart, orders, Razorpay test payments, reviews, messages, admin

Built on top of your `ramya` branch and tested with your real login system.
All 30 tests pass together with Shreshta's branch (interview, vision, pricing).

## New files
    backend/app/routers/cart.py       GET/POST /cart, DELETE /cart/{listing_id}
    backend/app/routers/orders.py     /orders/checkout, /orders/verify, /orders, /orders/sales, PATCH /orders/{id}/status
    backend/app/routers/reviews.py    POST /reviews, GET /reviews/seller/{id}
    backend/app/routers/messages.py   GET /chats, GET/POST /chats/{listing_id}/messages
    backend/app/routers/admin.py      /admin/stats, listings, review-queue, users, orders
    backend/app/razorpay_service.py   Razorpay test mode (mock mode when keys are blank)
    backend/app/schemas_market.py     request/response shapes (separate from schemas.py)
    backend/tests/test_market.py      tests for all of the above
    frontend/src/api/payments.js      opens the Razorpay popup; call payForCart() from the cart page

## Changed files (shared – tell Shreshta)
    backend/app/models.py     ADDED columns only: Order.seller_id, razorpay ids;
                              Review.reviewer_id/seller_id/created_at; Message.is_read;
                              CartItem.added_at + one-item-once rule
    backend/app/main.py       one import line + five include_router lines
    backend/app/deps.py       banned users get 403
    backend/requirements.txt  + razorpay, python-dotenv
    backend/.env.example      + RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

## IMPORTANT: delete your old database once
New columns were added, and SQLite won't add them to an existing file.
Delete backend/resell.db (if it exists). It is recreated on the next run.

## Status values
Order:   placed -> paid -> shipped -> delivered   (placed -> cancelled)
Listing: active, review (low AI confidence -> admin queue), sold, removed
User:    buyer, seller, admin, banned
