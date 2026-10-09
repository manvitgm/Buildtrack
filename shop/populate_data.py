"""
Populate the database with sample suppliers, categories, and materials.
Run:  python populate_data.py
"""
import os, sys, django, shutil

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.files import File
from customer.models import supplier, materialcategory, material

# ── Paths ──────────────────────────────────────────────────────
IMG_DIR = r"C:\Users\manvi\.gemini\antigravity\brain\0be7a3a9-e36f-4413-b98a-87330146dc19"

LOGO_FILES = {
    "ultratech":  "ultratech_logo_1779470298257.png",
    "steelcore":  "steelcore_logo_1779470313142.png",
    "brickzone":  "brickzone_logo_1779470331909.png",
    "greenwood":  "greenwood_logo_1779470348789.png",
    "aquaflow":   "aquaflow_logo_1779470362214.png",
    "powerelec":  "powerelec_logo_1779470376474.png",
}

MATERIAL_PHOTOS = {
    "cement":     "cement_bag_1779470401268.png",
    "steel":      "tmt_steel_bars_1779470416835.png",
    "bricks":     "red_bricks_1779470432945.png",
    "plywood":    "plywood_sheets_1779470449372.png",
    "pvc":        "pvc_pipes_1779470464370.png",
    "wire":       "electrical_wire_1779470479526.png",
    "sand":       "sand_aggregate_1779470497509.png",
    "paint":      "wall_paint_1779470515747.png",
}


def save_file_field(instance, field_name, src_filename, dest_name):
    """Copy a generated image into the model's FileField / ImageField."""
    src_path = os.path.join(IMG_DIR, src_filename)
    if not os.path.exists(src_path):
        print(f"  ⚠ Image not found: {src_path}")
        return
    with open(src_path, 'rb') as f:
        getattr(instance, field_name).save(dest_name, File(f), save=True)
    print(f"  ✅ Saved {field_name}: {dest_name}")


# ══════════════════════════════════════════════════════════════
# 1. SUPPLIERS
# ══════════════════════════════════════════════════════════════
SUPPLIERS_DATA = [
    {
        "key": "ultratech",
        "user": "Rajesh Kumar",
        "company_name": "UltraTech Cement Ltd.",
        "gst_number": "27AABCU9603R1ZM",
        "specialization": "Cement & Concrete",
        "warehouse_address": "Plot 45, MIDC Industrial Area, Pune, Maharashtra 411026",
        "rating": "5",
    },
    {
        "key": "steelcore",
        "user": "Amit Sharma",
        "company_name": "SteelCore Industries Pvt. Ltd.",
        "gst_number": "09AADCS4202K1Z4",
        "specialization": "TMT Bars & Structural Steel",
        "warehouse_address": "B-12, Steel Market, Mandi Gobindgarh, Punjab 147301",
        "rating": "4",
    },
    {
        "key": "brickzone",
        "user": "Suresh Patel",
        "company_name": "BrickZone Traders",
        "gst_number": "24AAFCB7891P1ZH",
        "specialization": "Bricks, Blocks & Masonry",
        "warehouse_address": "Survey No. 78, Morbi Road, Rajkot, Gujarat 360003",
        "rating": "4",
    },
    {
        "key": "greenwood",
        "user": "Vikram Mehta",
        "company_name": "GreenWood Timber Co.",
        "gst_number": "32AABCG5610L1ZK",
        "specialization": "Plywood, Timber & Wood Products",
        "warehouse_address": "Timber Yard, NH-66, Perumbavoor, Kerala 683542",
        "rating": "5",
    },
    {
        "key": "aquaflow",
        "user": "Priya Nair",
        "company_name": "AquaFlow Plumbing Solutions",
        "gst_number": "33AADCA3201M1Z9",
        "specialization": "PVC Pipes, Fittings & Plumbing",
        "warehouse_address": "44, Industrial Estate, Hosur Road, Bengaluru, Karnataka 560029",
        "rating": "4",
    },
    {
        "key": "powerelec",
        "user": "Deepak Verma",
        "company_name": "PowerElec Solutions",
        "gst_number": "07AABCP8821N1Z3",
        "specialization": "Electrical Wires, Cables & Fittings",
        "warehouse_address": "D-22, Bawana Industrial Area, New Delhi 110039",
        "rating": "5",
    },
]

print("\n🏭 Creating Suppliers...")
print("=" * 50)

created_suppliers = {}
for s_data in SUPPLIERS_DATA:
    key = s_data.pop("key")
    s, created = supplier.objects.get_or_create(
        company_name=s_data["company_name"],
        defaults=s_data,
    )
    if created:
        print(f"  ✅ Created: {s.company_name}")
    else:
        # Update existing record
        for k, v in s_data.items():
            setattr(s, k, v)
        s.save()
        print(f"  🔄 Updated: {s.company_name}")

    # Save logo
    if not s.logo:
        save_file_field(s, 'logo', LOGO_FILES[key], f"{key}_logo.png")

    created_suppliers[key] = s


# ══════════════════════════════════════════════════════════════
# 2. MATERIAL CATEGORIES
# ══════════════════════════════════════════════════════════════
CATEGORIES_DATA = [
    {"category_name": "Cement & Concrete",    "description": "OPC, PPC, Ready-mix concrete and binding materials",    "parent_category": "-"},
    {"category_name": "Steel & Iron",         "description": "TMT bars, structural steel, rebars and iron products",  "parent_category": "-"},
    {"category_name": "Bricks & Blocks",      "description": "Clay bricks, AAC blocks, fly ash bricks",               "parent_category": "-"},
    {"category_name": "Wood & Timber",        "description": "Plywood, timber, MDF boards and wood products",          "parent_category": "-"},
    {"category_name": "Plumbing",             "description": "PVC pipes, CPVC fittings, valves and plumbing hardware", "parent_category": "-"},
    {"category_name": "Electrical",           "description": "Wires, cables, switches, MCBs and electrical fittings",  "parent_category": "-"},
    {"category_name": "Sand & Aggregates",    "description": "River sand, M-sand, gravel, crushed stone",              "parent_category": "Cement & Concrete"},
    {"category_name": "Paints & Finishes",    "description": "Interior, exterior paints, primers and coatings",        "parent_category": "-"},
]

print("\n📦 Creating Categories...")
print("=" * 50)

created_categories = {}
for c_data in CATEGORIES_DATA:
    c, created = materialcategory.objects.get_or_create(
        category_name=c_data["category_name"],
        defaults=c_data,
    )
    status = "✅ Created" if created else "🔄 Exists"
    print(f"  {status}: {c.category_name}")
    created_categories[c.category_name] = c


# ══════════════════════════════════════════════════════════════
# 3. MATERIALS
# ══════════════════════════════════════════════════════════════
MATERIALS_DATA = [
    {
        "photo_key": "cement",
        "material_name": "UltraTech OPC 53 Grade Cement",
        "material_code": "CEM-OPC-53",
        "category_key": "Cement & Concrete",
        "supplier_key": "ultratech",
        "unit": "Bags (50kg)",
        "price": 420.00,
        "stock_quantity": 500,
        "description": "Premium OPC 53 Grade cement for high-strength construction. Ideal for RCC structures, bridges, and heavy-duty foundations. Achieves 53 MPa compressive strength in 28 days. ISI certified IS:12269.",
        "quality_status": "good",
    },
    {
        "photo_key": "steel",
        "material_name": "Fe-550D TMT Steel Bars (12mm)",
        "material_code": "STL-TMT-12",
        "category_key": "Steel & Iron",
        "supplier_key": "steelcore",
        "unit": "Tonnes",
        "price": 58500.00,
        "stock_quantity": 50,
        "description": "High-strength Fe-550D TMT reinforcement bars, 12mm diameter. Earthquake resistant with superior bendability. BIS certified IS:1786. Ideal for columns, beams, and slabs.",
        "quality_status": "good",
    },
    {
        "photo_key": "bricks",
        "material_name": "Premium Red Clay Bricks (Class A)",
        "material_code": "BRK-RED-A",
        "category_key": "Bricks & Blocks",
        "supplier_key": "brickzone",
        "unit": "Pieces (1000)",
        "price": 8500.00,
        "stock_quantity": 200,
        "description": "First-class red clay bricks with uniform color and sharp edges. Size: 230×110×75mm. Compressive strength > 10 N/mm². Water absorption < 15%. Ideal for load-bearing walls.",
        "quality_status": "good",
    },
    {
        "photo_key": "plywood",
        "material_name": "Marine Grade BWR Plywood (19mm)",
        "material_code": "PLY-BWR-19",
        "category_key": "Wood & Timber",
        "supplier_key": "greenwood",
        "unit": "Sheets (8x4 ft)",
        "price": 2850.00,
        "stock_quantity": 150,
        "description": "Boiling Water Resistant (BWR) marine grade plywood, 19mm thickness. Made from premium hardwood. IS:303 certified. Termite & borer treated. Perfect for kitchen cabinets and bathroom furniture.",
        "quality_status": "good",
    },
    {
        "photo_key": "pvc",
        "material_name": "ASTM PVC Pipes (4 inch, 6kg/cm²)",
        "material_code": "PVC-PIPE-4",
        "category_key": "Plumbing",
        "supplier_key": "aquaflow",
        "unit": "Pipes (3m each)",
        "price": 480.00,
        "stock_quantity": 300,
        "description": "Heavy-duty PVC pressure pipes, 4-inch (110mm) diameter, 6kg/cm² pressure rating. ASTM D1785 compliant. UV stabilized for outdoor use. Ideal for water supply and drainage systems.",
        "quality_status": "good",
    },
    {
        "photo_key": "wire",
        "material_name": "FR-LSH Copper Electrical Wire (2.5 sq mm)",
        "material_code": "ELC-CU-2.5",
        "category_key": "Electrical",
        "supplier_key": "powerelec",
        "unit": "Coils (90m)",
        "price": 3200.00,
        "stock_quantity": 100,
        "description": "Fire Retardant Low Smoke Halogen-free (FR-LSH) copper electrical wire, 2.5 sq mm. IS:694 certified. 1100V grade insulation. Color: Red. Ideal for domestic and commercial wiring.",
        "quality_status": "good",
    },
    {
        "photo_key": "sand",
        "material_name": "Manufactured Sand (M-Sand) - Plastering",
        "material_code": "SND-MSND-P",
        "category_key": "Sand & Aggregates",
        "supplier_key": "brickzone",
        "unit": "Cubic Feet",
        "price": 65.00,
        "stock_quantity": 5000,
        "description": "Premium quality manufactured sand for plastering applications. Dust-free and silt-free. Conforms to IS:383 Zone-II grading. Consistent quality with angular grain structure for better bonding.",
        "quality_status": "good",
    },
    {
        "photo_key": "paint",
        "material_name": "Premium Acrylic Emulsion Paint (20L)",
        "material_code": "PNT-ACR-20",
        "category_key": "Paints & Finishes",
        "supplier_key": "greenwood",
        "unit": "Buckets (20L)",
        "price": 4800.00,
        "stock_quantity": 80,
        "description": "Premium interior acrylic emulsion paint with silk smooth finish. Coverage: 120-140 sq ft per litre (2 coats). Low VOC, anti-fungal formula. Available in 1800+ shades. Washable up to 20,000 strokes.",
        "quality_status": "good",
    },
]

print("\n🧱 Creating Materials...")
print("=" * 50)

for m_data in MATERIALS_DATA:
    photo_key = m_data.pop("photo_key")
    category_key = m_data.pop("category_key")
    supplier_key = m_data.pop("supplier_key")

    m_data["category"] = created_categories[category_key]
    m_data["supplier"] = created_suppliers[supplier_key]

    m, created = material.objects.get_or_create(
        material_code=m_data["material_code"],
        defaults=m_data,
    )
    if created:
        print(f"  ✅ Created: {m.material_name}")
    else:
        print(f"  🔄 Exists: {m.material_name}")

    # Save product photo
    if not m.photo:
        photo_file = MATERIAL_PHOTOS.get(photo_key)
        if photo_file:
            src_path = os.path.join(IMG_DIR, photo_file)
            if os.path.exists(src_path):
                with open(src_path, 'rb') as f:
                    m.photo.save(f"{photo_key}_product.png", File(f), save=True)
                print(f"    📸 Photo saved for {m.material_name}")


# ══════════════════════════════════════════════════════════════
# ALSO UPDATE EXISTING SUPPLIERS WITH LOGOS
# ══════════════════════════════════════════════════════════════
print("\n🔄 Updating existing suppliers with logos...")
print("=" * 50)

# Map existing supplier names to logo keys
EXISTING_MAP = {
    "Ultratech": "ultratech",
    "TMT Steel bar": "steelcore",
    "UltraBuild Supplies": "brickzone",
    "SteelCore Pvt Ltd": "steelcore",
    "BrickZone Traders": "brickzone",
}

for name, logo_key in EXISTING_MAP.items():
    try:
        s = supplier.objects.get(company_name=name)
        if not s.logo:
            save_file_field(s, 'logo', LOGO_FILES[logo_key], f"{logo_key}_logo_{s.id}.png")
            print(f"  ✅ Logo added to existing supplier: {name}")
        else:
            print(f"  🔄 Already has logo: {name}")
    except supplier.DoesNotExist:
        pass


print("\n" + "=" * 50)
print("🎉 Done! Database populated successfully!")
print(f"   Suppliers: {supplier.objects.count()}")
print(f"   Categories: {materialcategory.objects.count()}")
print(f"   Materials: {material.objects.count()}")
print("=" * 50)
