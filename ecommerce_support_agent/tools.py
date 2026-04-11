"""
Mock e-commerce tools and database.
Swap these implementations with real DB/API calls in production.
"""

from datetime import datetime

# ---------------------------------------------------------------------------
# Mock database
# ---------------------------------------------------------------------------

ORDERS_DB = {
    "ORD-1001": {
        "customer_name": "Alice Johnson",
        "item": "Wireless Headphones",
        "status": "delivered",
        "order_date": "2025-03-25",
        "delivery_date": "2025-03-29",
        "price": 89.99,
        "carrier": "FedEx",
        "tracking_number": "FX-998877",
        "current_location": "Delivered to front door",
    },
    "ORD-1002": {
        "customer_name": "Bob Smith",
        "item": "Running Shoes",
        "status": "in_transit",
        "order_date": "2025-04-05",
        "delivery_date": "2025-04-12",
        "price": 124.95,
        "carrier": "UPS",
        "tracking_number": "UPS-334455",
        "current_location": "Chicago IL distribution center",
    },
    "ORD-1003": {
        "customer_name": "Carol White",
        "item": "Coffee Maker",
        "status": "processing",
        "order_date": "2025-04-08",
        "delivery_date": "2025-04-15",
        "price": 59.99,
        "carrier": "USPS",
        "tracking_number": "Not yet assigned",
        "current_location": "Warehouse",
    },
    "ORD-1004": {
        "customer_name": "David Lee",
        "item": "Mechanical Keyboard",
        "status": "delivered",
        "order_date": "2025-02-10",
        "delivery_date": "2025-02-14",
        "price": 149.00,
        "carrier": "FedEx",
        "tracking_number": "FX-112233",
        "current_location": "Delivered to mailbox",
    },
}

RETURN_WINDOW_DAYS = 30


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def lookup_order(order_id: str) -> dict:
    """Fetch order details from the database."""
    order = ORDERS_DB.get(order_id.upper())
    if not order:
        return {"found": False, "error": f"No order found with ID {order_id}"}
    return {
        "found": True,
        "order_id": order_id.upper(),
        "customer_name": order["customer_name"],
        "item": order["item"],
        "status": order["status"],
        "order_date": order["order_date"],
        "delivery_date": order["delivery_date"],
        "price": order["price"],
    }


def check_return_eligibility(order_id: str) -> dict:
    """Check whether an order is within the return window."""
    order = ORDERS_DB.get(order_id.upper())
    if not order:
        return {"found": False, "error": f"No order found with ID {order_id}"}

    if order["status"] != "delivered":
        return {
            "found": True,
            "eligible": False,
            "reason": f"Order is still '{order['status']}' — must be delivered before a return can be requested.",
        }

    delivery_date = datetime.strptime(order["delivery_date"], "%Y-%m-%d")
    days_since = (datetime.now() - delivery_date).days
    days_remaining = RETURN_WINDOW_DAYS - days_since

    if days_remaining <= 0:
        return {
            "found": True,
            "eligible": False,
            "reason": f"The {RETURN_WINDOW_DAYS}-day return window closed {abs(days_remaining)} days ago.",
        }

    return {
        "found": True,
        "eligible": True,
        "item": order["item"],
        "days_remaining": days_remaining,
        "refund_amount": order["price"],
        "reason": "Within return window.",
    }


def get_tracking_info(order_id: str) -> dict:
    """Get shipment carrier and location details."""
    order = ORDERS_DB.get(order_id.upper())
    if not order:
        return {"found": False, "error": f"No order found with ID {order_id}"}
    return {
        "found": True,
        "order_id": order_id.upper(),
        "item": order["item"],
        "carrier": order["carrier"],
        "tracking_number": order["tracking_number"],
        "current_location": order["current_location"],
        "estimated_delivery": order["delivery_date"],
        "status": order["status"],
    }
