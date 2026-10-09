"""
Download unique product images from free stock sources and update materials.
"""
import os, sys, django, urllib.request
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.files.base import ContentFile
from customer.models import material

# Free stock images from Unsplash (direct links to realistic, high-quality images)
# Every single URL is chosen to be completely unique and highly relevant to the specific material
UNIQUE_IMAGES = {
    16: ("cem-ppc-43", "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=600&q=80"),       # PPC Cement - concrete mix/construction site
    19: ("stl-tmt-08", "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?w=600&q=80"),       # TMT 8mm - rebar mesh/steel bars on site
    20: ("stl-bwr-18", "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=600&q=80"),       # Binding Wire - industrial steel wire coils
    22: ("brk-fly-std", "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=600&q=80"),      # Fly Ash Bricks - grey concrete masonry/blocks
    23: ("ply-mr-12", "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=600&q=80"),           # MR Plywood - clean wood veneer/board
    24: ("tmb-teak-p", "https://images.unsplash.com/photo-1541123437800-1bb1317badc2?w=600&q=80"),          # Teak Wood - textured teak timber planks
    25: ("pvc-cpvc-1", "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&q=80"),       # CPVC Pipes - plumber working / piping installations
    26: ("elc-arm-4", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80"),           # Armoured Cable - bundle of colored/heavy electrical cables
    27: ("elc-mod-6a", "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&q=80"),          # Modular Switches - modern light switch panel
}

print("Downloading unique images...")
print("=" * 50)

for mat_id, (code, url) in UNIQUE_IMAGES.items():
    try:
        m = material.objects.get(id=mat_id)
        print(f"  Downloading for ID={mat_id} [{m.material_name}]...")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=15)
        image_data = response.read()
        
        # Save as new unique photo
        filename = f"{code}_unique.jpg"
        m.photo.save(filename, ContentFile(image_data), save=True)
        print(f"    Done! Saved as {filename}")
    except Exception as e:
        print(f"    Error: {e}")

print(f"\n{'=' * 50}")
print("Image update complete!")
