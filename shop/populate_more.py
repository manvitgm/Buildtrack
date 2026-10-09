"""
Add 12 more materials to the database.
Run: python populate_more.py
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.files import File
from customer.models import supplier, materialcategory, material

IMG_DIR = r"C:\Users\manvi\.gemini\antigravity\brain\0be7a3a9-e36f-4413-b98a-87330146dc19"

# New images that were generated
NEW_PHOTOS = {
    "concrete":    "concrete_mixer_1779470877642.png",
    "steel_plate": "steel_plates_1779470892812.png",
    "aac":         "aac_blocks_1779470908535.png",
}

# Reuse existing images for materials without new photos
REUSE_PHOTOS = {
    "cement":  "cement_bag_1779470401268.png",
    "steel":   "tmt_steel_bars_1779470416835.png",
    "bricks":  "red_bricks_1779470432945.png",
    "plywood": "plywood_sheets_1779470449372.png",
    "pvc":     "pvc_pipes_1779470464370.png",
    "wire":    "electrical_wire_1779470479526.png",
    "sand":    "sand_aggregate_1779470497509.png",
    "paint":   "wall_paint_1779470515747.png",
}

ALL_PHOTOS = {**NEW_PHOTOS, **REUSE_PHOTOS}

# Get suppliers by company name
def get_supplier(name):
    try:
        return supplier.objects.get(company_name=name)
    except:
        return supplier.objects.first()

def get_category(name):
    try:
        return materialcategory.objects.get(category_name=name)
    except:
        c, _ = materialcategory.objects.get_or_create(
            category_name=name,
            defaults={"description": name, "parent_category": "-"}
        )
        return c


# ----------------------------------------------------------------
# NEW MATERIALS DATA
# ----------------------------------------------------------------
MATERIALS = [
    # -- UltraTech Cement --
    {
        "photo_key": "cement",
        "material_name": "UltraTech PPC Cement (Pozzolana)",
        "material_code": "CEM-PPC-43",
        "category": "Cement & Concrete",
        "supplier": "UltraTech Cement Ltd.",
        "unit": "Bags (50kg)",
        "price": 380.00,
        "stock_quantity": 800,
        "description": "Portland Pozzolana Cement with fly ash. Provides superior finish and long-term durability. Ideal for plastering, tiling, and masonry work. Lower heat of hydration. ISI certified IS:1489.",
        "quality_status": "good",
    },
    {
        "photo_key": "concrete",
        "material_name": "Ready-Mix Concrete M25 Grade",
        "material_code": "CEM-RMC-25",
        "category": "Cement & Concrete",
        "supplier": "UltraTech Cement Ltd.",
        "unit": "Cubic Meters",
        "price": 5200.00,
        "stock_quantity": 100,
        "description": "Factory-batched M25 grade ready-mix concrete. Compressive strength 25 MPa at 28 days. Consistent quality with precise water-cement ratio. Minimum order: 3 cubic meters. Delivery within 45 minutes.",
        "quality_status": "good",
    },

    # -- SteelCore Industries --
    {
        "photo_key": "steel_plate",
        "material_name": "MS Flat Bar 50x6mm",
        "material_code": "STL-FLAT-50",
        "category": "Steel & Iron",
        "supplier": "SteelCore Industries Pvt. Ltd.",
        "unit": "Pieces (6m)",
        "price": 750.00,
        "stock_quantity": 200,
        "description": "Mild Steel flat bar 50mm x 6mm, 6-meter length. IS:2062 Grade E250. Used for grills, gates, window frames, and structural fabrication. Hot-rolled with smooth finish.",
        "quality_status": "good",
    },
    {
        "photo_key": "steel",
        "material_name": "Fe-500D TMT Steel Bars (8mm)",
        "material_code": "STL-TMT-08",
        "category": "Steel & Iron",
        "supplier": "SteelCore Industries Pvt. Ltd.",
        "unit": "Tonnes",
        "price": 56000.00,
        "stock_quantity": 40,
        "description": "High-strength Fe-500D TMT bars, 8mm diameter. Ideal for slabs, lintels, and light RCC structures. Superior weldability and ductility. BIS certified IS:1786. Earthquake resistant.",
        "quality_status": "good",
    },
    {
        "photo_key": "steel",
        "material_name": "Binding Wire (18 Gauge)",
        "material_code": "STL-BWR-18",
        "category": "Steel & Iron",
        "supplier": "SteelCore Industries Pvt. Ltd.",
        "unit": "Kg",
        "price": 72.00,
        "stock_quantity": 1000,
        "description": "Black annealed binding wire, 18 gauge (1.2mm). Soft and flexible for easy tying of reinforcement bars. Rust-resistant coating. Sold per kg. Coil weight: 25kg each.",
        "quality_status": "good",
    },

    # -- BrickZone Traders --
    {
        "photo_key": "aac",
        "material_name": "AAC Blocks (600x200x200mm)",
        "material_code": "BRK-AAC-200",
        "category": "Bricks & Blocks",
        "supplier": "BrickZone Traders",
        "unit": "Pieces",
        "price": 55.00,
        "stock_quantity": 5000,
        "description": "Autoclaved Aerated Concrete blocks, size 600x200x200mm. Lightweight, fire-resistant, and excellent thermal insulation. Replaces 8 regular bricks. Reduces construction time by 30%. IS:2185 certified.",
        "quality_status": "good",
    },
    {
        "photo_key": "bricks",
        "material_name": "Fly Ash Bricks (Standard Size)",
        "material_code": "BRK-FLY-STD",
        "category": "Bricks & Blocks",
        "supplier": "BrickZone Traders",
        "unit": "Pieces (1000)",
        "price": 6200.00,
        "stock_quantity": 300,
        "description": "Eco-friendly fly ash bricks, size 230x110x75mm. High compressive strength (7.5 N/mm2). Low water absorption. Uniform shape and size. No plastering required in many cases.",
        "quality_status": "average",
    },

    # -- GreenWood Timber --
    {
        "photo_key": "plywood",
        "material_name": "Commercial Grade MR Plywood (12mm)",
        "material_code": "PLY-MR-12",
        "category": "Wood & Timber",
        "supplier": "GreenWood Timber Co.",
        "unit": "Sheets (8x4 ft)",
        "price": 1650.00,
        "stock_quantity": 200,
        "description": "Moisture Resistant (MR) grade commercial plywood, 12mm thickness. IS:303 certified. Suitable for interior furniture, partitions, and false ceilings. Termite treated.",
        "quality_status": "good",
    },
    {
        "photo_key": "plywood",
        "material_name": "Teak Wood Planks (Premium Grade)",
        "material_code": "TMB-TEAK-P",
        "category": "Wood & Timber",
        "supplier": "GreenWood Timber Co.",
        "unit": "Cubic Feet",
        "price": 3800.00,
        "stock_quantity": 60,
        "description": "Premium Burma Teak wood planks, naturally seasoned. Rich golden-brown color with straight grain. Highly durable and termite-resistant. Ideal for doors, window frames, and luxury furniture.",
        "quality_status": "good",
    },

    # -- AquaFlow Plumbing --
    {
        "photo_key": "pvc",
        "material_name": "CPVC Hot Water Pipes (1 inch)",
        "material_code": "PVC-CPVC-1",
        "category": "Plumbing",
        "supplier": "AquaFlow Plumbing Solutions",
        "unit": "Pipes (3m each)",
        "price": 320.00,
        "stock_quantity": 400,
        "description": "CPVC pipes for hot and cold water supply, 1-inch (25mm) diameter. Withstands water temperature up to 93 degrees C. Lead-free, non-toxic. ASTM D2846 compliant. 50-year service life.",
        "quality_status": "good",
    },

    # -- PowerElec Solutions --
    {
        "photo_key": "wire",
        "material_name": "3-Phase Armoured Cable (4 sq mm)",
        "material_code": "ELC-ARM-4",
        "category": "Electrical",
        "supplier": "PowerElec Solutions",
        "unit": "Meters",
        "price": 280.00,
        "stock_quantity": 500,
        "description": "3.5-core armoured copper cable, 4 sq mm. Steel wire armoured for underground and outdoor installations. PVC insulated, 1100V grade. IS:1554 certified. Ideal for main power supply lines.",
        "quality_status": "good",
    },
    {
        "photo_key": "wire",
        "material_name": "Modular Switches & Sockets (6A, Set of 10)",
        "material_code": "ELC-MOD-6A",
        "category": "Electrical",
        "supplier": "PowerElec Solutions",
        "unit": "Sets (10 pcs)",
        "price": 1200.00,
        "stock_quantity": 150,
        "description": "Premium modular electrical switches and sockets, 6A rated. Polycarbonate body with silver contact points. Fire-retardant material. Includes 5 switches + 5 sockets. Sleek white design. ISI marked.",
        "quality_status": "good",
    },
]

print("\n--- Adding 12 More Materials ---")
print("=" * 50)

added = 0
for m_data in MATERIALS:
    photo_key = m_data.pop("photo_key")
    cat_name = m_data.pop("category")
    sup_name = m_data.pop("supplier")

    m_data["category"] = get_category(cat_name)
    m_data["supplier"] = get_supplier(sup_name)

    m, created = material.objects.get_or_create(
        material_code=m_data["material_code"],
        defaults=m_data,
    )

    if created:
        added += 1
        print(f"  [+] {m.material_name}")

        # Save photo
        photo_file = ALL_PHOTOS.get(photo_key)
        if photo_file:
            src = os.path.join(IMG_DIR, photo_file)
            if os.path.exists(src):
                with open(src, 'rb') as f:
                    m.photo.save(f"{m.material_code.lower()}_photo.png", File(f), save=True)
                print(f"      Photo saved")
    else:
        print(f"  [=] Already exists: {m.material_name}")

print(f"\n{'=' * 50}")
print(f"Done! Added {added} new materials.")
print(f"Total materials in DB: {material.objects.count()}")
print(f"Total suppliers: {supplier.objects.count()}")
print(f"Total categories: {materialcategory.objects.count()}")
print(f"{'=' * 50}")
