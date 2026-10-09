import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from customer.views import material_suggestions
from django.test import RequestFactory
rf = RequestFactory()
req = rf.get('/material_suggestions/?q=a')
res = material_suggestions(req)
print(res.content.decode())
