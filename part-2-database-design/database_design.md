Part 2: Database Design

1. companies
Represents each business using the platform
companies (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
)
•	id
Unique identifier for each company. UUIDs support scalability and multi-tenant safety.
•	name
Stores the official company name.
•	created_at
Tracks when the company was created for auditing and analytics.

2. warehouses
A company can own multiple warehouses
warehouses (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    location TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
company_id
 Links each warehouse to its owning company.
name
 Human-readable warehouse name.
location
 Physical address or geographic information.
Relationship:
One company → many warehouses
Why this design:
Supports real-world scenarios where a business operates multiple storage locations.

3. products
Products are global to a company and can exist in multiple warehouses
products (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    is_bundle BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    UNIQUE (company_id, sku),
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
sku
 Business-critical identifier used for inventory and integrations.
price
 Uses DECIMAL to avoid floating-point precision errors.
is_bundle
 Identifies whether the product is a bundle.
UNIQUE (company_id, sku)
 Prevents SKU duplication within the same company.
Why this design:
Products are company-scoped but warehouse-agnostic, allowing flexible inventory placement.

4. inventory
Tracks quantity of a product in a specific warehouse
inventory (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL,
    warehouse_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE (product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
)
quantity
 Stores current stock level.
UNIQUE (product_id, warehouse_id)
 Ensures only one inventory record per product per warehouse.
Relationship:
Product ↔ Warehouse (many-to-many via inventory)
Why this design:
Allows products to be stocked in multiple warehouses without data duplication.

5. inventory_movements
Tracks when and how inventory levels change
inventory_movements (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL,
    warehouse_id UUID NOT NULL,
    change_quantity INTEGER NOT NULL,
    reason VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
)
change_quantity
 Positive or negative inventory change.
reason
 Explains why the change occurred.
Example reasons:
STOCK_IN, SALE, TRANSFER, ADJUSTMENT
Why this design:
Provides a complete audit trail for compliance, debugging, and reporting.

6. suppliers
Suppliers that provide products
suppliers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info TEXT,
    created_at TIMESTAMP NOT NULL
)
contact_info
 Stores email, phone, or address details.
Why this design:
Keeps supplier data centralized and reusable across products.

7. supplier_products
Many-to-many relationship between suppliers and products
supplier_products (
    supplier_id UUID NOT NULL,
    product_id UUID NOT NULL,
    PRIMARY KEY (supplier_id, product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
Composite primary key
 Prevents duplicate supplier-product mappings.
Why this design:
A supplier can provide many products, and a product can have multiple suppliers.

8. product_bundles
Defines bundle composition
product_bundles (
    bundle_product_id UUID NOT NULL,
    component_product_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (bundle_product_id, component_product_id),
    FOREIGN KEY (bundle_product_id) REFERENCES products(id),
    FOREIGN KEY (component_product_id) REFERENCES products(id)
)
bundle_product_id
 The bundled product.
component_product_id
 Individual product inside the bundle.
quantity
 Number of each component required.
Meaning:
A bundle product is composed of multiple component products.


Missing Requirements / Questions for Product Team
•	Is SKU unique globally or per company?
•	Can inventory quantities go negative (backorders)?
•	Should warehouse transfers be atomic?
•	Can suppliers belong to multiple companies?
•	Do we track supplier pricing and lead times?
•	Can bundles contain other bundles?
•	Does selling a bundle auto-deduct component inventory?
•	How long should inventory movement history be retained?
•	Is pricing multi-currency?


Design Decisions & Justification
•	Inventory as a separate table
 Enables multi-warehouse support and scalability.
•	Inventory movements table
 Ensures traceability and audit compliance.
•	Unique constraints
 Enforce business rules and data integrity.
•	Self-referencing bundle design
 Flexible and avoids data duplication.
•	UUID primary keys
 Ideal for distributed, multi-tenant SaaS systems.
