Code Issues Identified and Corrections Explained
1. Missing request body validation
What was wrong:
The original code directly accessed request.json and assumed valid input.
What was added:
data = request.get_json()
if not data:
    return {"error": "Invalid JSON payload"}, 400
Why it was added:
Prevents server crashes when empty or malformed JSON is sent and ensures graceful error handling.

2. Required fields not validated
What was wrong:
Fields like name and sku were accessed without checking existence.
What was added:
if 'name' not in data or 'sku' not in data:
    return {"error": "Missing required fields"}, 400
Why it was added:
Avoids runtime KeyError and enforces minimum product creation requirements.

3. SKU uniqueness not enforced
What was wrong:
The system allowed multiple products with the same SKU.
What was added:
if Product.query.filter_by(sku=data['sku']).first():
    return {"error": "SKU already exists"}, 409
Why it was added:
Ensures SKU uniqueness, which is critical for inventory tracking and integrations.

4. Incorrect product–warehouse relationship
What was wrong:
Product was directly tied to a single warehouse_id.
What was changed:
product = Product(
    name=data['name'],
    sku=data['sku'],
    price=price
)
Why it was changed:
Allows products to exist across multiple warehouses and keeps inventory responsibility in the Inventory table.

5. Unsafe price handling
What was wrong:
Price was accepted directly, risking floating-point precision issues.
What was added:
price = Decimal(str(data['price']))
Why it was added:
Ensures accurate financial calculations using decimal precision.

6. Initial quantity not validated
What was wrong:
Negative inventory values were possible.
What was added:
if initial_quantity < 0:
    return {"error": "Initial quantity cannot be negative"}, 400
Why it was added:
Prevents invalid stock states and maintains inventory integrity.

7. Multiple commits causing partial data writes
What was wrong:
Product and inventory were committed separately.
What was changed:
with db.session.begin():
Why it was added:
Wraps both operations in a single atomic transaction to prevent partial data persistence.

8. Product ID accessed before safe commit
What was wrong:
Product ID depended on a commit.
What was added:
db.session.flush()
Why it was added:
Generates the product ID without committing, allowing safe inventory creation in the same transaction.

9. Inventory created without warehouse check
What was wrong:
Inventory was created even if warehouse data was missing.
What was added:
if warehouse_id:
Why it was added:
Supports optional inventory creation and flexible product onboarding.

10. No error handling or HTTP status codes
What was wrong:
API always returned success regardless of failures.
What was added:
except IntegrityError:
    return {"error": "Database constraint violation"}, 409
Why it was added:
Provides meaningful feedback to clients and improves API reliability.

