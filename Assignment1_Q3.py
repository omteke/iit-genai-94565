import csv
import re
from statistics import mean

FILENAME = "Products.csv"

# candidate header names for automatic detection (lowercase)
CANDIDATES = {
    "id": ["id", "productid", "product_id", "pid", "prodid"],
    "name": ["name", "productname", "product_name", "title"],
    "category": ["category", "cat", "category_name", "type"],
    "price": ["price", "mrp", "cost", "amount", "rate", "unit_price"],
    "quantity": ["quantity", "qty", "stock", "quantity_in_stock", "qty_in_stock", "amount_in_stock"]
}

def clean_key(k): 
    return k.strip().lower()

def find_column(headers_lower, candidates_list):
    # Exact match first, then substring match
    for c in candidates_list:
        if c in headers_lower:
            # return the original header name that matched
            for orig, low in headers_map.items():
                if low == c:
                    return orig
    # substring fallback
    for c in candidates_list:
        for orig, low in headers_map.items():
            if c in low:
                return orig
    return None

def parse_price(s):
    if s is None: 
        return None
    s = str(s).strip()
    if s == "": 
        return None
    # remove currency symbols, commas, and spaces
    s = re.sub(r'[^\d.\-]', '', s)
    if s in ("", ".", "-", "-."):
        return None
    try:
        return float(s)
    except ValueError:
        return None

def parse_int(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None
    s = re.sub(r'[^\d\-]', '', s)
    try:
        return int(s)
    except ValueError:
        return None

# ---------- (a) Read CSV ----------
products = []
with open(FILENAME, mode="r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    # normalize header keys (strip) but preserve original keys
    for row in reader:
        # strip whitespace from keys and values
        clean_row = {}
        for k, v in row.items():
            if k is None:
                continue
            clean_keyname = k.strip()
            clean_row[clean_keyname] = v.strip() if isinstance(v, str) else v
        products.append(clean_row)

if not products:
    print("No rows found in the CSV (after header). Exiting.")
    raise SystemExit

# show actual CSV headers
orig_headers = list(products[0].keys())
print("CSV Columns detected:", orig_headers)

# prepare lowercase map for detection
headers_map = {orig: clean_key(orig) for orig in orig_headers}
headers_lower_set = set(headers_map.values())

# detect columns
id_col = find_column(headers_lower_set, CANDIDATES["id"])
name_col = find_column(headers_lower_set, CANDIDATES["name"])
cat_col = find_column(headers_lower_set, CANDIDATES["category"])
price_col = find_column(headers_lower_set, CANDIDATES["price"])
qty_col = find_column(headers_lower_set, CANDIDATES["quantity"])

print("\nAuto-detected mapping:")
print(f"  ID column:       {id_col}")
print(f"  Name column:     {name_col}")
print(f"  Category column: {cat_col}")
print(f"  Price column:    {price_col}")
print(f"  Quantity column: {qty_col}")

# ---------- (b) Print each row in a clean format ----------
print("\n--- Product List ---")
for i, p in enumerate(products, start=1):
    idv = p.get(id_col) if id_col else None
    namev = p.get(name_col) if name_col else None
    catv = p.get(cat_col) if cat_col else None
    pricev = p.get(price_col) if price_col else None
    qtyv = p.get(qty_col) if qty_col else None
    print(f"{i:>3}. ID: {idv} | Name: {namev} | Category: {catv} | Price: {pricev} | Quantity: {qtyv}")

# ---------- (c) Total number of rows ----------
total_rows = len(products)
print("\nTotal number of rows:", total_rows)

# ---------- prepare numeric fields ----------
prices = []
qtys = []
price_missing_count = 0
qty_missing_count = 0

for p in products:
    raw_price = p.get(price_col) if price_col else None
    parsed_price = parse_price(raw_price)
    if parsed_price is None:
        price_missing_count += 1
    else:
        prices.append(parsed_price)

    raw_qty = p.get(qty_col) if qty_col else None
    parsed_qty = parse_int(raw_qty)
    if parsed_qty is None:
        qty_missing_count += 1
    else:
        qtys.append(parsed_qty)

# ---------- (d) Total number of products priced above 500 ----------
if prices:
    above_500 = sum(1 for pr in prices if pr > 500)
    print("Products priced above 500:", above_500)
else:
    print("Cannot compute 'priced above 500' — no valid numeric prices found.")

# ---------- (e) Average price of all products ----------
if prices:
    avg_price = mean(prices)
    print("Average price of products: {:.2f}".format(avg_price))
    if price_missing_count:
        print(f"  (Note: {price_missing_count} rows had missing/invalid price and were skipped.)")
else:
    print("Cannot compute average price — no valid numeric prices found.")

# ---------- (f) List products belonging to a specific category ----------
if not cat_col:
    print("\nCannot filter by category — no category column detected.")
else:
    user_input = input("\nEnter category to filter (case-insensitive): ").strip().lower()
    matched = []
    for p in products:
        catv = p.get(cat_col)
        if catv and user_input in catv.strip().lower():
            namev = p.get(name_col) if name_col else "(unknown name)"
            matched.append((namev, p.get(price_col)))
    print(f"\nProducts in category matching '{user_input}':")
    if matched:
        for namev, pricev in matched:
            print(f" - {namev}  | Price: {pricev}")
    else:
        print("  No products matched that category.")

# ---------- (g) Total quantity of all items in stock ----------
if qtys:
    total_qty = sum(qtys)
    print("\nTotal quantity of all items in stock:", total_qty)
    if qty_missing_count:
        print(f"  (Note: {qty_missing_count} rows had missing/invalid quantity and were skipped.)")
else:
    print("\nCannot compute total quantity — no valid numeric quantities found.")
