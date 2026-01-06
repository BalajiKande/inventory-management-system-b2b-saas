from decimal import Decimal, InvalidOperation        # ADDED
from sqlalchemy.exc import IntegrityError            # ADDED
from flask import request

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()                         # CHANGED

    if not data:                                     # ADDED
        return {"error": "Invalid JSON payload"}, 400

    if 'name' not in data or 'sku' not in data:      # ADDED
        return {"error": "Missing required fields"}, 400

    price = None                                     # ADDED
    if 'price' in data:                              # ADDED
        try:
            price = Decimal(str(data['price']))      # ADDED
        except (InvalidOperation, TypeError):        # ADDED
            return {"error": "Invalid price format"}, 400

    initial_quantity = data.get('initial_quantity', 0)  # CHANGED
    if initial_quantity < 0:                          # ADDED
        return {"error": "Initial quantity cannot be negative"}, 400

    warehouse_id = data.get('warehouse_id')           # CHANGED

    try:
        if Product.query.filter_by(sku=data['sku']).first():  # ADDED
            return {"error": "SKU already exists"}, 409

        with db.session.begin():                      # ADDED
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=price                           # CHANGED
            )
            db.session.add(product)
            db.session.flush()                        # ADDED

            if warehouse_id:                          # ADDED
                inventory = Inventory(
                    product_id=product.id,
                    warehouse_id=warehouse_id,
                    quantity=initial_quantity
                )
                db.session.add(inventory)

        return {
            "message": "Product created successfully",
            "product_id": product.id
        }, 201                                        # CHANGED

    except IntegrityError:                            # ADDED
        db.session.rollback()
        return {"error": "Database constraint violation"}, 409

    except Exception:                                 # ADDED
        db.session.rollback()
        return {"error": "Internal server error"}, 500
