import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from customer.models import supplier

NEW_SUPPLIERS = [
    {
        "user": "Nisha Gupta",
        "company_name": "Gupta Hardware & Tools",
        "gst_number": "06AABCG8811K1Z2",
        "specialization": "Fasteners, Tools & Hardware",
        "warehouse_address": "Shop No 15, Hardware Market, Chawri Bazar, New Delhi 110006",
        "rating": "4.5",
    },
    {
        "user": "Manish Tiwari",
        "company_name": "Tiwari Glass Works",
        "gst_number": "09AADCT9922M1Z5",
        "specialization": "Toughened Glass & Aluminium Profiles",
        "warehouse_address": "Sector 63, Noida, Uttar Pradesh 201301",
        "rating": "4.8",
    },
    {
        "user": "Sunita Reddy",
        "company_name": "Deccan Paints & Chemicals",
        "gst_number": "36AAECD2233N1Z8",
        "specialization": "Industrial Paints, Primers & Waterproofing",
        "warehouse_address": "Plot 112, IDA Jeedimetla, Hyderabad, Telangana 500055",
        "rating": "4.2",
    },
    {
        "user": "Mohammed Ali",
        "company_name": "Ali Stone Crushers",
        "gst_number": "29AABCA5544L1Z9",
        "specialization": "Aggregates, Gravel & Crushed Stone",
        "warehouse_address": "Sy No 45, Outskirts Road, Bidadi, Karnataka 562109",
        "rating": "4.6",
    },
    {
        "user": "Rohit Desai",
        "company_name": "Desai Tiles & Ceramics",
        "gst_number": "27AABCD6655P1Z1",
        "specialization": "Floor Tiles, Wall Tiles & Sanitaryware",
        "warehouse_address": "Gala No 5, Ceramic Zone, Morbi, Gujarat 363642",
        "rating": "4.9",
    }
]

print("Adding more suppliers...")
added = 0
for s_data in NEW_SUPPLIERS:
    s, created = supplier.objects.get_or_create(
        company_name=s_data["company_name"],
        defaults=s_data
    )
    if created:
        print(f"  [+] Created: {s.company_name}")
        added += 1
    else:
        print(f"  [=] Exists: {s.company_name}")

print(f"\nSuccessfully added {added} new suppliers.")
print(f"Total suppliers in DB: {supplier.objects.count()}")
