Implementation:
from flask import Flask, jsonify
from datetime import datetime, timedelta
import psycopg2

app = Flask(__name__)

@app.route("/api/companies/<company_id>/alerts/low-stock", methods=["GET"])
def low_stock_alerts(company_id):
    """
    Returns low-stock alerts for a company across all warehouses.
    """

    conn = psycopg2.connect("dbname=inventory_db user=postgres password=secret")
    cursor = conn.cursor()

    # Assumption: Recent sales = last 30 days
    recent_date = datetime.utcnow() - timedelta(days=30)

    query = """
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.sku,
            w.id AS warehouse_id,
            w.name AS warehouse_name,
            i.quantity AS current_stock,
            t.threshold,
            s.id AS supplier_id,
            s.name AS supplier_name,
            s.contact_info,
            COALESCE(SUM(ABS(im.change_quantity)), 0) / 30.0 AS avg_daily_sales
        FROM inventory i
        JOIN products p ON p.id = i.product_id
        JOIN warehouses w ON w.id = i.warehouse_id
        JOIN product_thresholds t ON t.product_id = p.id
        JOIN inventory_movements im
            ON im.product_id = p.id
            AND im.warehouse_id = w.id
            AND im.reason = 'SALE'
            AND im.created_at >= %s
        LEFT JOIN supplier_products sp ON sp.product_id = p.id
        LEFT JOIN suppliers s ON s.id = sp.supplier_id
        WHERE p.company_id = %s
        GROUP BY
            p.id, w.id, i.quantity, t.threshold, s.id
        HAVING i.quantity < t.threshold
    """

    cursor.execute(query, (recent_date, company_id))
    rows = cursor.fetchall()

    alerts = []

    for row in rows:
        avg_daily_sales = row[10]

        # Edge case: No recent sales → skip alert
        if avg_daily_sales <= 0:
            continue

        days_until_stockout = int(row[6] / avg_daily_sales)

        alerts.append({
            "product_id": row[0],
            "product_name": row[1],
            "sku": row[2],
            "warehouse_id": row[3],
            "warehouse_name": row[4],
            "current_stock": row[5],
            "threshold": row[6],
            "days_until_stockout": days_until_stockout,
            "supplier": {
                "id": row[7],
                "name": row[8],
                "contact_email": row[9]
            }
        })

    cursor.close()
    conn.close()

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    })

