"""
tools.py
--------
Defines external tool functions for the ReAct Agent scenario:
TechWarehouse Order & Shipping Logistics Assistant.
"""

from typing import Dict, Any, Union


# Mock Inventory Database
INVENTORY_DB = {
    "PROD-9042": {
        "name": "Model-X Drone",
        "price": 499.00,
        "stock": 14,
        "warehouse": "WH-East",
        "weight_kg": 4.2
    },
    "PROD-3011": {
        "name": "Quantum Keyboard",
        "price": 85.00,
        "stock": 3,  # Only 3 in stock! (Used for fulfillability test)
        "warehouse": "WH-Central",
        "weight_kg": 1.5
    },
    "PROD-1001": {
        "name": "Wireless Earbuds",
        "price": 45.00,
        "stock": 50,
        "warehouse": "WH-West",
        "weight_kg": 0.3
    },
    "PROD-1002": {
        "name": "Smartwatch",
        "price": 120.00,
        "stock": 25,
        "warehouse": "WH-West",
        "weight_kg": 0.5
    }
}


def check_inventory(product_id: str) -> Dict[str, Any]:
    """
    Look up real-time inventory stock levels, unit price, and warehouse location for a product.
    
    Args:
        product_id (str): The product ID (e.g., 'PROD-9042', 'PROD-3011').
        
    Returns:
        dict: Product details including stock, price, warehouse, and weight.
    """
    product_id_upper = product_id.strip().upper()
    if product_id_upper in INVENTORY_DB:
        info = INVENTORY_DB[product_id_upper]
        return {
            "status": "success",
            "product_id": product_id_upper,
            "name": info["name"],
            "unit_price": info["price"],
            "stock_count": info["stock"],
            "warehouse": info["warehouse"],
            "unit_weight_kg": info["weight_kg"]
        }
    else:
        return {
            "status": "error",
            "message": f"Product ID '{product_id}' not found in inventory system."
        }


def calculate_shipping_rate(weight_kg: float, destination_zip: str, service_type: str = "standard") -> Dict[str, Any]:
    """
    Calculate live shipping costs and estimated delivery transit days.
    
    Args:
        weight_kg (float): Total weight of the package in kilograms.
        destination_zip (str): Destination postal/ZIP code.
        service_type (str): 'standard', 'expedited', or 'expedited_cold'.
        
    Returns:
        dict: Calculated shipping fee, transit time in days, and service details.
    """
    try:
        weight = float(weight_kg)
    except (ValueError, TypeError):
        return {"status": "error", "message": f"Invalid weight value: {weight_kg}"}

    service = service_type.strip().lower()
    
    # Base rates matrix
    if service == "standard":
        base_rate = 8.00
        per_kg_rate = 2.50
        est_days = 5 if weight < 10.0 else 7
    elif service == "expedited":
        base_rate = 18.00
        per_kg_rate = 4.00
        est_days = 3
    elif service == "expedited_cold" or service == "expedited cold":
        base_rate = 30.00
        per_kg_rate = 4.50
        est_days = 2
    else:
        return {"status": "error", "message": f"Unknown service type '{service_type}'. Valid: standard, expedited, expedited_cold."}

    total_shipping_cost = round(base_rate + (weight * per_kg_rate), 2)

    return {
        "status": "success",
        "destination_zip": str(destination_zip),
        "service_type": service,
        "weight_kg": weight,
        "shipping_cost_usd": total_shipping_cost,
        "estimated_transit_days": est_days
    }


def check_shipping_policy(order_weight_kg: float, contains_perishable: bool) -> Dict[str, Any]:
    """
    Queries shipping policy rules based on order weight and whether items are perishable electronics.
    
    Args:
        order_weight_kg (float): Weight of the shipment in kg.
        contains_perishable (bool): Whether the package contains temperature-sensitive electronics.
        
    Returns:
        dict: Required shipping tier, max delivery SLA, and cold shipping rule enforcement.
    """
    try:
        weight = float(order_weight_kg)
    except (ValueError, TypeError):
        return {"status": "error", "message": f"Invalid weight: {order_weight_kg}"}
        
    perishable = bool(contains_perishable)

    if weight > 5.0 and perishable:
        return {
            "status": "success",
            "required_shipping_tier": "Expedited Cold Shipping",
            "mandatory_reason": "Perishable electronics over 5 kg require temperature control.",
            "transit_days": 2,
            "base_cost_usd": 30.00
        }
    elif perishable:
        return {
            "status": "success",
            "required_shipping_tier": "Expedited Shipping",
            "mandatory_reason": "Perishable electronics under 5 kg require fast handling.",
            "transit_days": 3,
            "base_cost_usd": 18.00
        }
    else:
        return {
            "status": "success",
            "required_shipping_tier": "Standard Shipping",
            "mandatory_reason": "Non-perishable standard items.",
            "transit_days": 5,
            "base_cost_usd": 8.00
        }


# Map of tool names to functions for ReAct dispatch
AVAILABLE_TOOLS = {
    "check_inventory": check_inventory,
    "calculate_shipping_rate": calculate_shipping_rate,
    "check_shipping_policy": check_shipping_policy
}
