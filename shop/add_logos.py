import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.files import File
from customer.models import supplier
from PIL import Image, ImageDraw, ImageFont

# Ensure a media/documents directory exists
os.makedirs('media/documents', exist_ok=True)

SUPPLIERS = [
    ("Gupta Hardware & Tools", "GHT", "#1f77b4"),
    ("Tiwari Glass Works", "TGW", "#ff7f0e"),
    ("Deccan Paints & Chemicals", "DPC", "#2ca02c"),
    ("Ali Stone Crushers", "ASC", "#d62728"),
    ("Desai Tiles & Ceramics", "DTC", "#9467bd"),
]

def generate_logo(initials, bg_color, output_path):
    # Create a 400x400 image
    img = Image.new('RGB', (400, 400), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Try to load a nice font, or fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except IOError:
        font = ImageFont.load_default()
        
    # We will just center the text using simple math or getbbox
    try:
        bbox = d.textbbox((0, 0), initials, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older PIL
        text_w, text_h = d.textsize(initials, font=font)
        
    x = (400 - text_w) / 2
    y = (400 - text_h) / 2
    
    d.text((x, y), initials, fill="white", font=font)
    img.save(output_path)


print("Generating and assigning logos...")
for name, initials, color in SUPPLIERS:
    try:
        s = supplier.objects.get(company_name=name)
        filename = f"{initials.lower()}_logo.png"
        filepath = os.path.join('media', 'documents', filename)
        
        generate_logo(initials, color, filepath)
        
        with open(filepath, 'rb') as f:
            s.logo.save(filename, File(f), save=True)
            
        print(f"  [+] Logo added for: {name}")
    except supplier.DoesNotExist:
        print(f"  [-] Supplier not found: {name}")

print("Finished adding logos.")
