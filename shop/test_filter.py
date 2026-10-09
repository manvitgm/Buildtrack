import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from customer.models import material
from django.db.models import Q

q = 'a'
results = material.objects.filter(
    Q(material_name__icontains=q) |
    Q(material_code__icontains=q) |
    Q(category__category_name__icontains=q)
)
print('Results:', results.count())
