# Task split (two people, equal load)

Deadline: around 24 Nov. Each person owns separate files, so Git conflicts stay rare.

## Ramya: Marketplace (CRUD and basics)
| When | Task | Files |
|---|---|---|
| Sun 22 (today) | Project skeleton, all DB tables, auth, listings CRUD, search and filters, image upload | DONE in this starter |
| Mon 23 | Cart, orders and order status, Razorpay test-mode payment, reviews and ratings, buyer-seller messaging, admin moderation | `routers/cart.py`, `orders.py`, `reviews.py`, `messages.py`, `admin.py` |
| Tue 24 | React pages: login/register, browse and search, listing detail, create listing, cart and checkout, my orders, admin | `frontend/src/pages/...` |

## Friend: AI and Intelligence (the unique features)
| When | Task | Files |
|---|---|---|
| Sun 22 night / Mon 23 | AI seller interview (category-specific questions, transcript), grading engine (score, grade A-D, confidence, low confidence goes to manual review) | `routers/interview.py`, `grading.py`, `services/` |
| Mon 23 | Defect detection with a vision model on listing images, duplicate-image check, condition report saved to `condition_reports` | `services/vision.py` |
| Mon 23 | Price engine: comparables by model and grade, median and spread, Great deal / Fair / Overpriced, seed data | `routers/price.py`, `services/price_engine.py` |
| Tue 24 | Chrome extension (Manifest V3) Fair Price Meter, React interview and report pages, evaluation table, README diagram, demo video | `extension/`, `frontend/src/pages/Interview*` |

## Shared files (tell each other before editing)
- `backend/app/models.py`: add columns carefully, never rename or delete.
- `backend/app/main.py`: only add one `include_router` line.

## API contract between you two
- Friend's grading code calls `listing.grade = "B"; listing.grade_score = 82; listing.status = "active" or "review"`.
- Ramya's search already filters by `grade`, so the work joins up with no extra code.
