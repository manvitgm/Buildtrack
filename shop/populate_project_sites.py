import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from customer.models import userregistration, projectsite

# Create a user first
admin_user, created = userregistration.objects.get_or_create(
    email="admin@example.com",
    defaults={
        "name": "Admin User",
        "password": "password123",
        "contact": "9876543210",
        "city": "Mumbai",
        "role": "admin"
    }
)
if created:
    print(f"Created Admin User: {admin_user.name}")

# Create project sites
PROJECT_SITES = [
    {
        "site_name": "Skyline Residency",
        "manager": "Rajesh Kumar",
        "location": "Andheri West, Mumbai",
        "latitude": 19.1136,
        "longitude": 72.8697,
        "project_type": "Residential Complex",
        "start_date": "2023-01-15",
        "expected_end_date": "2025-06-30",
        "status": "In Progress",
        "created_by": admin_user,
        "approval_status": "approved",
    },
    {
        "site_name": "TechPark Phase 2",
        "manager": "Suresh Patel",
        "location": "Hinjewadi, Pune",
        "latitude": 18.5913,
        "longitude": 73.7389,
        "project_type": "Commercial IT Park",
        "start_date": "2022-05-10",
        "expected_end_date": "2024-12-15",
        "status": "In Progress",
        "created_by": admin_user,
        "approval_status": "approved",
    },
    {
        "site_name": "Green Valley Villas",
        "manager": "Amit Sharma",
        "location": "Lonavala",
        "latitude": 18.7481,
        "longitude": 73.4072,
        "project_type": "Luxury Villas",
        "start_date": "2024-02-01",
        "expected_end_date": "2026-03-31",
        "status": "Planning",
        "created_by": admin_user,
        "approval_status": "pending",
    }
]

added = 0
for site_data in PROJECT_SITES:
    p, p_created = projectsite.objects.get_or_create(
        site_name=site_data["site_name"],
        defaults=site_data
    )
    if p_created:
        added += 1
        print(f"Created Project Site: {p.site_name}")
    else:
        print(f"Project Site exists: {p.site_name}")

print(f"Total project sites: {projectsite.objects.count()}")
