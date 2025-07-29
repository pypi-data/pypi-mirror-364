import sqlite3
import json
import datetime
import os
from typing import Dict, List, Any, Optional
from zoneinfo import ZoneInfo
from send_email_utils import send_email
from logger import log

# Configuration
DB = "inventory.db"
JSON_FILE = "annual_po.json"

def current_ist_time_str() -> str:
    return datetime.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

def query(sql: str, params: tuple = (), fetch: bool = True) -> Optional[List[Dict]]:
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch:
            result = cur.fetchall()
            return [dict(row) for row in result] if result else []
        conn.commit()

def calculate_expiry_days(expiry_date: str) -> int:
    try:
        expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        today = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).date()
        return (expiry - today).days
    except ValueError:
        return 0

def init_db():
    is_new = not os.path.exists(DB)

    with sqlite3.connect(DB) as conn:
        if is_new:
            conn.execute("""
                CREATE TABLE medicines (
                    drugId TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    genericName TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    batchNumber TEXT NOT NULL,
                    expiryDate DATE NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    unit TEXT NOT NULL,
                    pricePerUnit REAL DEFAULT 0.0,
                    location TEXT NOT NULL,
                    expiry_days INTEGER DEFAULT 0,
                    stock_alert_threshold INTEGER DEFAULT 10,
                    added_on DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.executescript("""
                CREATE INDEX idx_generic_name ON medicines(genericName);
                CREATE INDEX idx_name ON medicines(name);
                CREATE INDEX idx_expiry ON medicines(expiryDate);
                CREATE INDEX idx_quantity ON medicines(quantity);
                CREATE INDEX idx_expiry_days ON medicines(expiry_days);
            """)
            conn.commit()
            log("DB initialized")
            
            # Load dummy data ONLY on first database creation
            load_dummy_data()

def load_dummy_data():
    if not os.path.exists(JSON_FILE):
        return
    try:
        with open(JSON_FILE) as f:
            data = json.load(f)
            success_count = 0
            for item in data:
                result = add_med(item)
                if result.get("status") == "success":
                    success_count += 1
                else:
                    log("Dummy data load error", f"{item.get('drugId', 'Unknown')}: {result.get('message')}")
            print(f"Dummy data loaded. {success_count} medicines added.")
            log("Dummy data loaded", f"{success_count} out of {len(data)} medicines added successfully")
    except json.JSONDecodeError as e:
        log("Error loading dummy data", str(e))

def send_stock_alert(drug_id: str, medicine_name: str, current_stock: int, action: str):
    alert_type = "OUT OF STOCK" if current_stock == 0 else "LOW STOCK"
    subject = f"🚨 INVENTORY ALERT: {alert_type} - {medicine_name}"
    body = f"""
URGENT INVENTORY ALERT
======================

Medicine: {medicine_name}
Drug ID: {drug_id}
Current Stock: {current_stock} units
Alert Type: {alert_type}
Action Performed: {action}
Date/Time: {current_ist_time_str()}

{"⚠️  IMMEDIATE ACTION REQUIRED: This medicine is completely out of stock!" if current_stock == 0 else "⚠️  WARNING: This medicine is running low on stock."}

This is an automated alert from the Medicine Inventory Management System.
"""
    return send_email(subject, body, "manager")

def send_restock_request(drug_id: str, medicine_name: str, manufacturer: str, current_stock: int, requested_quantity: int = 100):
    subject = f"🔄 RESTOCK REQUEST: {medicine_name}"
    body = f"""
MEDICINE RESTOCK REQUEST
========================

Dear Supplier,

We are running low on the following medicine and need to place a restock order:

- Name: {medicine_name}
- Drug ID: {drug_id}
- Manufacturer: {manufacturer}
- Current Stock: {current_stock} units
- Requested Quantity: {requested_quantity} units

Please confirm availability and provide:
1. Price quotation
2. Delivery timeline
3. Batch details

Contact:
- Email: {os.getenv('MANAGER_EMAIL')}
- Phone: {os.getenv('MANAGER_PHONE', 'N/A')}

Date/Time: {current_ist_time_str()}
"""
    return send_email(subject, body, "supplier")

# CRUD Operations

def read_med(args: Dict[str, Any]) -> Dict[str, Any]:
    term = args.get("input", "").strip()
    if not term:
        return {"status": "error", "message": "Missing 'input'"}
    meds = query("SELECT * FROM medicines WHERE name LIKE ? OR genericName LIKE ?", 
                 (f"%{term}%", f"%{term}%"))
    log("Medicine Read", term)
    return {"status": "success", "results": meds, "count": len(meds)}

def add_med(args: Dict[str, Any]) -> Dict[str, Any]:
    required_args = [
        "drugId", "name", "genericName", "manufacturer", "batchNumber",
        "expiryDate", "quantity", "unit", "pricePerUnit", "location"
    ]

    missing = [arg for arg in required_args if not args.get(arg)]
    if missing:
        return {"status": "error", "message": f"Missing fields: {', '.join(missing)}"}

    try:
        quantity = int(args["quantity"])
        price_per_unit = float(args["pricePerUnit"])
    except (ValueError, TypeError):
        return {"status": "error", "message": "Invalid 'quantity' or 'pricePerUnit' format"}

    expiry_days = calculate_expiry_days(args["expiryDate"])
    stock_threshold = int(args.get("stock_alert_threshold", 10))
    now = current_ist_time_str()

    query("""
        INSERT OR REPLACE INTO medicines (
            drugId, name, genericName, manufacturer, batchNumber,
            expiryDate, quantity, unit, pricePerUnit, location,
            expiry_days, stock_alert_threshold,
            added_on, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        args["drugId"], args["name"], args["genericName"], args["manufacturer"],
        args["batchNumber"], args["expiryDate"], quantity,
        args["unit"], price_per_unit, args["location"],
        expiry_days, stock_threshold, now, now
    ), fetch=False)

    log("Medicine Added/Updated", f"{args['drugId']}: {args['name']} ({quantity} {args['unit']})")
    return {"status": "success", "message": f"Medicine '{args['name']}' added successfully"}

def update_med(args: Dict[str, Any]) -> Dict[str, Any]:
    required = ["input", "quantity"]
    missing = [k for k in required if k not in args or args[k] in (None, "", [])]
    if missing:
        return {"status": "error", "message": f"Missing fields: {', '.join(missing)}"}

    try:
        # Validate quantity
        try:
            delta_qty = int(args["quantity"])
        except Exception:
            return {"status": "error", "message": "Invalid 'quantity', must be an integer"}

        if delta_qty == 0:
            return {"status": "error", "message": "Quantity must be non-zero"}

        term = args["input"].strip()
        med_search = read_med({"input": term})
        if med_search["status"] != "success":
            return {"status": "error", "message": "Medicine lookup failed"}

        meds = med_search.get("results", [])
        if len(meds) == 0:
            return {"status": "error", "message": f"No medicines found matching '{term}'"}
        elif len(meds) > 1:
            choices = [
                f"{m['drugId']}: {m['name']} ({m['genericName']}) - {m.get('manufacturer', 'Unknown')}, Stock: {m['quantity']}"
                for m in meds
            ]
            return {
                "status": "ambiguous",
                "message": "Multiple medicines found. Please specify the correct one.",
                "choices": choices
            }

        med = meds[0]
        drug_id = med["drugId"]
        name = med["name"]
        old_qty = med["quantity"]
        threshold = med.get("stock_alert_threshold", 10)

        if delta_qty < 0 and old_qty < abs(delta_qty):
            return {
                "status": "error",
                "message": f"Cannot remove {abs(delta_qty)} units. Only {old_qty} available.",
                "details": {
                    "drugId": drug_id,
                    "name": name,
                    "available": old_qty
                }
            }

        new_qty = max(0, old_qty + delta_qty)
        query("UPDATE medicines SET quantity=?, last_updated=? WHERE drugId=?", 
              (new_qty, current_ist_time_str(), drug_id), fetch=False)

        action = "added" if delta_qty > 0 else "removed"
        log(f"Quantity {action.capitalize()}", f"{drug_id}: {old_qty} → {new_qty}")

        alert_sent = False
        if delta_qty < 0 and new_qty <= threshold:
            alert_sent = send_stock_alert(drug_id, name, new_qty, f"Removed {abs(delta_qty)} units")

        return {
            "status": "success",
            "message": f"{abs(delta_qty)} units {action} for '{name}'",
            "details": {
                "drugId": drug_id,
                "name": name,
                "old_quantity": old_qty,
                "new_quantity": new_qty,
                "action": action,
                "alert_sent": alert_sent
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_alert(args: Dict[str, Any]) -> Dict[str, Any]:
    required = ["input", "stock_alert_threshold"]
    missing = [k for k in required if k not in args or args[k] in (None, "", [])]
    if missing:
        return {"status": "error", "message": f"Missing fields: {', '.join(missing)}"}

    term = args["input"].strip()
    try:
        threshold = int(args["stock_alert_threshold"])
        if threshold <= 0:
            raise ValueError("Threshold must be a positive number")
    except Exception:
        return {"status": "error", "message": "Invalid 'stock_alert_threshold', must be a positive integer"}

    try:
        med_search = read_med({"input": term})
        if med_search["status"] != "success":
            return {"status": "error", "message": "Medicine lookup failed"}

        meds = med_search.get("results", [])
        if len(meds) == 0:
            return {"status": "error", "message": f"No medicines found matching '{term}'"}
        elif len(meds) > 1:
            choices = [
                f"{m['drugId']}: {m['name']} ({m['genericName']}) - {m.get('manufacturer', 'Unknown')}, Stock: {m['quantity']}"
                for m in meds
            ]
            return {
                "status": "ambiguous",
                "message": "Multiple medicines found. Please specify the correct one.",
                "choices": choices
            }
        med = meds[0]
        query("UPDATE medicines SET stock_alert_threshold=?, last_updated=? WHERE drugId=?", 
              (threshold, current_ist_time_str(), med["drugId"]), fetch=False)
        log(f"Alert threshold set to {threshold} for '{med['name']}'")

        return {
            "status": "success",
            "message": f"Alert threshold set to {threshold} for '{med['name']}'",
            "details": {
                "drugId": med["drugId"],
                "name": med["name"],
                "stock_alert_threshold": threshold
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_med(args: Dict[str, Any]) -> Dict[str, Any]:
    if "input" not in args or not args["input"].strip():
        return {"status": "error", "message": "Missing or empty 'input' field"}

    term = args["input"].strip()

    try:
        med_search = read_med({"input": term})
        if med_search["status"] != "success":
            return {"status": "error", "message": "Medicine lookup failed"}

        meds = med_search.get("results", [])
        if len(meds) == 0:
            return {"status": "error", "message": f"No medicines found matching '{term}'"}
        elif len(meds) > 1:
            choices = [
                f"{m['drugId']}: {m['name']} ({m['genericName']}) - {m.get('manufacturer', 'Unknown')}, Stock: {m['quantity']}"
                for m in meds
            ]
            return {
                "status": "ambiguous",
                "message": "Multiple medicines found. Please specify the correct one.",
                "choices": choices
            }
        med = meds[0]
        query("DELETE FROM medicines WHERE drugId=?", (med["drugId"],), fetch=False)
        log("Deleted", f"{med['drugId']} - {med['name']}")

        return {
            "status": "success",
            "message": f"Medicine '{med['name']}' deleted successfully",
            "details": {
                "drugId": med["drugId"],
                "name": med["name"]
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_restock_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    required = ["medicine_name", "requested_stock"]
    missing = [k for k in required if k not in args]
    if missing:
        return {"status": "error", "message": f"Missing fields: {', '.join(missing)}"}

    try:
        med_search = read_med({"input": args["medicine_name"]})
        if med_search["status"] != "success":
            return {"status": "error", "message": "Medicine lookup failed"}

        meds = med_search.get("results", [])
        if len(meds) == 0:
            return {"status": "error", "message": f"No medicines found matching '{args['medicine_name']}'"}
        elif len(meds) > 1:
            choices = [
                f"{m['drugId']}: {m['name']} ({m['genericName']}) - {m['manufacturer']}, Stock: {m['quantity']}"
                for m in meds
            ]
            return {
                "status": "ambiguous",
                "message": "Multiple medicines found. Please specify the correct one.",
                "choices": choices
            }
        med = meds[0]
        result = send_restock_request(
            med["drugId"], med["name"], med.get("manufacturer", "Unknown"), int(med["quantity"]), int(args["requested_stock"])
        )
        return {"status": "success", "message": "Restock email sent", "email_result": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_expiring_medicines_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        days_threshold = int(args.get("days_threshold", 30))
        sql = """
            SELECT * FROM medicines 
            WHERE expiry_days <= ? AND expiry_days >= 0 
            ORDER BY expiry_days
        """
        result = query(sql, (days_threshold,))
        return {
            "status": "success",
            "message": f"Medicines expiring in {days_threshold} days or less.",
            "results": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def get_expired_medicines_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        sql = """
            SELECT * FROM medicines 
            WHERE expiry_days < 0 
            ORDER BY expiry_days
        """
        result = query(sql)
        return {
            "status": "success",
            "message": "List of already expired medicines.",
            "results": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_expiry_days() -> int:
    meds = query("SELECT drugId, expiryDate FROM medicines")
    for med in meds:
        days = calculate_expiry_days(med["expiryDate"])
        query("UPDATE medicines SET expiry_days=? WHERE drugId=?", (days, med["drugId"]), fetch=False)
    log("Updated expiry days", f"{len(meds)} entries")
    return len(meds)

# Tool definitions for the agent
TOOLS = {
    "read_med": {
        "func": read_med,
        "required_args": ["input"],
        "description": "Read medicine details by name or generic name."
    },
    "add_med": {
        "func": add_med,
        "required_args": ["drugId", "name", "genericName", "manufacturer", "batchNumber", "expiryDate", "quantity", "unit", "pricePerUnit", "location"],
        "description": "Add a medicine in the inventory. Requires complete medicine data with all required fields mentioned."
    },
    "update_med": {
        "func": update_med,
        "required_args": ["input", "quantity"],
        "description": "Add or remove (if quantity is negative) stock of a medicine using its name or generic name."
    },
    "set_alert": {
        "func": set_alert,
        "required_args": ["input", "stock_alert_threshold"],
        "description": "Set custom stock alert threshold for a medicine by name or generic name."
    },
    "delete_med": {
        "func": delete_med,
        "required_args": ["input"],
        "description": "Delete medicine entry completely from inventory by name or generic name."
    },
    "send_restock_request": {
        "func": send_restock_tool,
        "required_args": ["medicine_name", "requested_stock"],
        "description": "Send a restock email request to supplier for a specific medicine."
    },
    "get_expiring_medicines": {
        "func": get_expiring_medicines_tool,
        "required_args": [],
        "optional_args": ["days_threshold"],
        "description": "Fetch medicines that are expiring within a given number of days (default is 30 days)."
    },
    "get_expired_medicines": {
        "func": get_expired_medicines_tool,
        "required_args": [],
        "description": "Fetch all medicines that have already expired."
    }
}

init_db()