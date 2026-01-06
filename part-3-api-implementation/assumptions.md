Problem Understanding (In Simple Words)
The goal of this API is to warn a company when products are running low, but only when it actually matters.
That means:
•	Different products have different low-stock thresholds
•	Alerts should only be shown for products that are actively selling
•	Stock can be spread across multiple warehouses
•	Alerts should include supplier info so reordering is easy
This is not just a technical API — it’s a business-critical decision tool.

Key Assumptions (Because Requirements Are Incomplete)
Since some details were not provided, I made the following reasonable assumptions and documented them clearly:
1.	Low-stock threshold
Stored in a product_thresholds table based on product type
Example: fast-moving items have higher thresholds
2.	Recent sales activity
A product is considered “active” if it had at least one SALE movement in the last 30 days
3.	Days until stockout
Calculated using average daily sales from the last 30 days
4.	Supplier
The primary supplier is selected arbitrarily if multiple suppliers exist
5.	Stock is tracked per warehouse
Alerts are generated per product per warehouse


Technology Choice
•	Python + Flask
•	Clean, readable, and commonly used for backend APIs
•	SQL assumed (PostgreSQL-style queries)

API Endpoint
GET /api/companies/{company_id}/alerts/low-stock
