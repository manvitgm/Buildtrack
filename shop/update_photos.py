import os, sys, django, glob
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.files import File
from customer.models import material

# Directory where images are saved
IMG_DIR = r"C:\Users\manvi\.gemini\antigravity\brain\eead197b-7b45-4ac3-99ed-6542d5b453bb"

MAPPING = {
    "cement_opc_53": 1,
    "tmt_bars_12mm": 2,
    "red_clay_bricks": 3,
    "plywood_19mm": 4,
    "pvc_pipes_4inch": 5,
    "electrical_wire_red": 6,
    "manufactured_sand": 7,
    "paint_bucket_20l": 8,
    "cement_ppc": 9,
    "ready_mix_concrete": 10,
    "ms_flat_bars": 11,
    "tmt_bars_8mm": 12,
    "binding_wire": 13,
    "aac_blocks": 14,
    "fly_ash_bricks": 15,
    "plywood_12mm": 16,
    "teak_wood_planks": 17,
}

# Find actual filenames
updated_count = 0
for key, mat_id in MAPPING.items():
    # Find file matching key_*.png
    matches = glob.glob(os.path.join(IMG_DIR, f"{key}_*.png"))
    if matches:
        file_path = matches[0]
        try:
            m = material.objects.get(id=mat_id)
            with open(file_path, 'rb') as f:
                m.photo.save(f"{key}.png", File(f), save=True)
            print(f"Updated photo for: {m.material_name}")
            updated_count += 1
        except material.DoesNotExist:
            print(f"Material ID {mat_id} not found.")

print(f"\nSuccessfully updated photos for {updated_count} materials.")
