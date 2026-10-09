from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
import random
import re
import string
import io
import base64
from django.contrib.auth.hashers import make_password, check_password
from PIL import Image, ImageDraw, ImageFont
from .models import *


# ============================================================
# SESSION HELPERS
# ============================================================

def check_login(request):
    return 'uid' in request.session


def get_current_user(request):
    try:
        return userregistration.objects.get(id=request.session['uid'])
    except:
        return None


def send_notification(user, title, message):
    """Helper: auto-create notification for any event"""
    notification.objects.create(
        user=user,
        title=title,
        message=message,
    )


def _create_captcha_image(text):
    """Generate a CAPTCHA PNG image and return as a base64 data URI."""
    width, height = 220, 70
    img = Image.new('RGB', (width, height), color=(248, 250, 252)) # Light background
    draw = ImageDraw.Draw(img)

    # Draw background noise lines
    for _ in range(8):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        color = (random.randint(200, 230), random.randint(200, 230), random.randint(200, 230))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 2))

    # Draw noise dots
    for _ in range(150):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        draw.point((x, y), fill=(random.randint(150, 200), random.randint(150, 200), random.randint(150, 200)))

    # Load font
    font = None
    for font_name in ['arial.ttf', 'Arial.ttf', 'DejaVuSans-Bold.ttf', 'FreeSansBold.ttf']:
        try:
            font = ImageFont.truetype(font_name, 38)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    # Dark/vivid color palette for characters on light background
    dark_colors = [
        (0, 100, 200),    # Dark blue
        (200, 0, 100),    # Crimson
        (0, 150, 50),     # Dark green
        (150, 50, 200),   # Purple
        (220, 80, 0),     # Burnt orange
        (30, 40, 50),     # Charcoal
    ]

    # Draw each character with random position & dark color
    x_pos = 15
    for char in text:
        color = random.choice(dark_colors)
        y_pos = random.randint(8, 22)
        draw.text((x_pos, y_pos), char, font=font, fill=color)
        x_pos += random.randint(28, 36)

    # Draw foreground noise lines over text
    for _ in range(4):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Convert to base64 data URI
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{img_b64}'


def _generate_captcha(request):
    """Generate new CAPTCHA: store text in session, return image data URI."""
    # Use uppercase letters + digits, remove confusing chars (0/O, 1/I/L)
    chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    captcha_text = ''.join(random.choices(chars, k=6))
    request.session['captcha_text'] = captcha_text
    return _create_captcha_image(captcha_text)


def refresh_captcha(request):
    """AJAX endpoint: generate a new CAPTCHA and return the image as JSON."""
    captcha_image = _generate_captcha(request)
    return JsonResponse({'image': captcha_image})


def is_admin(request):
    """Check if the logged-in user is an admin"""
    return request.session.get('user_role') == 'admin'


def admin_required(request):
    """
    Redirect staff users away from admin-only pages.
    Returns True if user is NOT admin (i.e. should be blocked).
    Usage:  if admin_required(request): return redirect(...)
    """
    if not check_login(request):
        return True
    if not is_admin(request):
        messages.error(request, "⛔ Access denied. Admin privileges required.")
        return True
    return False


# ============================================================
# HOME
# ============================================================

def frontpage(request):
    # Fetch real-time metrics for the landing page dashboard
    total_materials = material.objects.count()
    total_suppliers = supplier.objects.count()
    total_orders = materialorder.objects.count()
    total_sites = projectsite.objects.count()
    
    # Calculate real-time Stock Available percentage
    in_stock_count = material.objects.filter(stock_quantity__gt=0).count()
    stock_percentage = int((in_stock_count / total_materials * 100)) if total_materials > 0 else 100
    
    # Get 3 featured materials with their photos and suppliers to display as a live catalog preview
    featured_materials = material.objects.all().order_by('-id')[:3]
    
    # Fetch 3 latest live reviews from database
    latest_reviews = review.objects.select_related('reviewer', 'supplier', 'material').order_by('-id')[:3]
    
    context = {
        'total_materials': total_materials,
        'total_suppliers': total_suppliers,
        'total_orders': total_orders,
        'total_sites': total_sites,
        'stock_percentage': stock_percentage,
        'featured_materials': featured_materials,
        'latest_reviews': latest_reviews,
    }
    return render(request, "frontpage.html", context)



# ============================================================
# LOGIN
# ============================================================

# Admin secret key — change this to your own secret!
ADMIN_SECRET_KEY = "BUILDTRACK@2026"


def insertlogin(request):
    if request.method == "POST":
        # Verify CAPTCHA
        user_captcha = request.POST.get('captcha', '').strip().upper()
        session_captcha = request.session.get('captcha_text', '')
        if not user_captcha or user_captcha != session_captcha:
            messages.error(request, "⚠️ Incorrect CAPTCHA. Please try again.")
            return redirect('/insertlogin/')

        email = request.POST.get("email")
        password = request.POST.get("password")
        login_type = request.POST.get("login_type", "staff")

        try:
            user = userregistration.objects.get(email=email)

            # Check hashed password OR fallback to plaintext for migration
            if check_password(password, user.password):
                pass
            elif password == user.password:
                user.password = make_password(password)
                user.save()
            else:
                messages.error(request, "Invalid email or password.")
                return redirect('/insertlogin/')

            # ── ADMIN PANEL LOGIN ──────────────────────────
            if login_type == "admin":
                admin_key = request.POST.get("admin_key", "")
                if admin_key != ADMIN_SECRET_KEY:
                    messages.error(request, "⛔ Invalid Admin Secret Key.")
                    return redirect('/insertlogin/')
                if user.role != 'admin':
                    messages.error(request, "⛔ This account does not have admin privileges.")
                    return redirect('/insertlogin/')

            # ── STAFF PANEL LOGIN ──────────────────────────
            if login_type == "staff" and user.role == 'admin':
                # Admin accounts must use the admin panel
                messages.error(request, "Admin accounts must sign in via the Admin Panel tab.")
                return redirect('/insertlogin/')

            request.session['uid'] = user.id
            request.session['uname'] = user.name
            request.session['user_role'] = user.role
            return redirect('/dashboard/')
        except userregistration.DoesNotExist:
            messages.warning(request, "No account found with this email. Please register to create a new account.")
            return redirect('/insertuserregistration/')
    captcha_image = _generate_captcha(request)
    return render(request, "login.html", {'captcha_image': captcha_image})


# ============================================================
# LOGOUT
# ============================================================

def logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('/insertlogin/')


# ============================================================
# FORGOT PASSWORD & OTP
# ============================================================

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = userregistration.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            
            # SIMULATING EMAIL SENDING
            messages.success(request, f"OTP sent to {email}. (For demo purposes, the OTP is: {otp})")
            return redirect('/verify_otp/')
        except userregistration.DoesNotExist:
            messages.error(request, "No account found with that email address.")
            return redirect('/forgot_password/')
    return render(request, "forgot_password.html")

def verify_otp(request):
    if 'reset_email' not in request.session:
        return redirect('/forgot_password/')

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if entered_otp == request.session.get('reset_otp'):
            request.session['otp_verified'] = True
            messages.success(request, "OTP verified! Please set a new password.")
            return redirect('/reset_password/')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('/verify_otp/')
    return render(request, "verify_otp.html")

def reset_password(request):
    if not request.session.get('otp_verified'):
        return redirect('/forgot_password/')

    email = request.session.get('reset_email')
    
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/reset_password/')
            
        if not is_strong_password(new_password):
            messages.error(request, "Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character.")
            return redirect('/reset_password/')
            
        try:
            user = userregistration.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            
            # Clear session keys
            request.session.pop('reset_otp', None)
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)
            
            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect('/insertlogin/')
        except userregistration.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('/forgot_password/')
            
    return render(request, "reset_password.html")


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(request):
    if not check_login(request):
        return redirect('/insertlogin/')

    user = get_current_user(request)
    unread_count = notification.objects.filter(user=user, is_read=False).count() if user else 0

    # Calculate realistic metrics
    orders = materialorder.objects.all()
    if not is_admin(request):
        orders = orders.filter(ordered_by=user)
    
    total_revenue = orders.exclude(order_status='cancelled').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_orders = orders.filter(order_status__in=['placed', 'processing']).count()
    completed_orders = orders.filter(order_status='delivered').count()

    # Generate 7 days of mock data for charts to make it look realistic
    import datetime
    today = datetime.date.today()
    last_7_days = [(today - datetime.timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    
    import random
    revenue_chart_data = [random.randint(5000, 35000) for _ in range(7)]
    orders_chart_data = [random.randint(2, 15) for _ in range(7)]

    context = {
        'total_materials': material.objects.count(),
        'total_suppliers': supplier.objects.count(),
        'total_orders': orders.count(),
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_users': userregistration.objects.count(),
        'recent_orders': orders.order_by('-id')[:6],
        'low_stock': material.objects.filter(stock_quantity__lte=10)[:4],
        'unread_notifications': unread_count,
        'is_admin': is_admin(request),
        'chart_labels': last_7_days,
        'revenue_chart_data': revenue_chart_data,
        'orders_chart_data': orders_chart_data,
    }
    return render(request, "index.html", context)


# ============================================================
# USER REGISTRATION
# ============================================================

def is_strong_password(password):
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"\d", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

def insertuserregistration(request):
    if request.method == "POST":
        # Verify CAPTCHA
        user_captcha = request.POST.get('captcha', '').strip().upper()
        session_captcha = request.session.get('captcha_text', '')
        if not user_captcha or user_captcha != session_captcha:
            messages.error(request, "⚠️ Incorrect CAPTCHA. Please try again.")
            return redirect('/insertuserregistration/')

        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "staff")
        
        if userregistration.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('/insertuserregistration/')

        if not is_strong_password(password):
            messages.error(request, "Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character.")
            return redirect('/insertuserregistration/')

        contact = request.POST.get("contact", "")
        city = request.POST.get("city", "")

        # Validate contact is exactly 10 digits
        if not re.match(r'^\d{10}$', contact):
            messages.error(request, "⚠️ Contact number must be exactly 10 digits (numbers only).")
            return redirect('/insertuserregistration/')

        # Validate city contains characters only (alphabetic + spaces)
        if not re.match(r'^[A-Za-z\s]+$', city):
            messages.error(request, "⚠️ City must contain letters and spaces only.")
            return redirect('/insertuserregistration/')

        # Admin registration requires the secret key
        if role == "admin":
            admin_key = request.POST.get("admin_key", "")
            if admin_key != ADMIN_SECRET_KEY:
                messages.error(request, "⛔ Invalid Admin Secret Key. You cannot register as admin without authorization.")
                return redirect('/insertuserregistration/')

        userregistration.objects.create(
            name=request.POST.get("name"),
            email=email,
            password=make_password(password),
            contact=request.POST.get("contact"),
            city=request.POST.get("city"),
            role=role,
            staff_role=request.POST.get("staff_role") if role == 'staff' else None,
        )
        messages.success(request, "Registration successful! Please login.")
        return redirect('/insertlogin/')
    captcha_image = _generate_captcha(request)
    return render(request, "userregistration.html", {'captcha_image': captcha_image})


def viewuserregistration(request):
    if admin_required(request):
        return redirect('/dashboard/')
    data = userregistration.objects.all()
    return render(request, "showregistration.html", {'data': data})


def delusereg(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    userregistration.objects.get(pk=pk).delete()
    messages.success(request, "User deleted.")
    return redirect('/viewuserregistration/')


# ============================================================
# SUPPLIER
# ============================================================

def insertsupplier(request):
    if admin_required(request):
        return redirect('/dashboard/')
    if request.method == "POST":
        supplier.objects.create(
            user=request.POST.get("user"),
            company_name=request.POST.get("company_name"),
            gst_number=request.POST.get("gst_number"),
            specialization=request.POST.get("specialization"),
            warehouse_address=request.POST.get("warehouse_address"),
            rating=request.POST.get("rating"),
            logo=request.FILES.get("logo"),
        )
        messages.success(request, "Supplier added.")
        return redirect('/viewsupplier/')
    return render(request, "supplier.html")


def viewsupplier(request):
    if not check_login(request):
        return redirect('/insertlogin/')
    data = supplier.objects.all()
    return render(request, "showsupplier.html", {'data': data})


def editsupplier(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    data = get_object_or_404(supplier, pk=pk)
    if request.method == "POST":
        data.user = request.POST.get("user")
        data.company_name = request.POST.get("company_name")
        data.gst_number = request.POST.get("gst_number")
        data.specialization = request.POST.get("specialization")
        data.warehouse_address = request.POST.get("warehouse_address")
        data.rating = request.POST.get("rating")
        if request.FILES.get("logo"):
            data.logo = request.FILES.get("logo")
        data.save()
        messages.success(request, "Supplier updated.")
        return redirect('/viewsupplier/')
    return render(request, "editsupplier.html", {'x': data})


def delsupp(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    supplier.objects.get(pk=pk).delete()
    messages.success(request, "Supplier deleted.")
    return redirect('/viewsupplier/')


# ============================================================
# MATERIAL CATEGORY
# ============================================================

def insertmaterialcategory(request):
    if admin_required(request):
        return redirect('/dashboard/')
    if request.method == "POST":
        materialcategory.objects.create(
            category_name=request.POST.get("category_name"),
            description=request.POST.get("description"),
            parent_category=request.POST.get("parent_category"),
        )
        messages.success(request, "Category added.")
        return redirect('/viewmaterialcategory/')
    return render(request, "materialcategory.html", {'categories': materialcategory.objects.all()})


def viewmaterialcategory(request):
    if not check_login(request):
        return redirect('/insertlogin/')
    return render(request, "showmaterialcategory.html", {'data': materialcategory.objects.all()})


def delmaterialcategory(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    materialcategory.objects.get(pk=pk).delete()
    messages.success(request, "Category deleted.")
    return redirect('/viewmaterialcategory/')


def editmaterialcategory(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    data = get_object_or_404(materialcategory, pk=pk)
    if request.method == "POST":
        data.category_name = request.POST.get("category_name")
        data.description = request.POST.get("description")
        data.parent_category = request.POST.get("parent_category")
        data.save()
        messages.success(request, "Category updated.")
        return redirect('/viewmaterialcategory/')
    return render(request, "editmaterialcategory.html", {
        'x': data,
        'categories': materialcategory.objects.exclude(id=pk)
    })


# ============================================================
# MATERIAL
# ============================================================

def insertmaterial(request):
    if admin_required(request):
        return redirect('/dashboard/')
    if request.method == "POST":
        material.objects.create(
            material_name=request.POST.get("material_name"),
            material_code=request.POST.get("material_code"),
            supplier=supplier.objects.get(id=request.POST.get("supplier")),
            category=materialcategory.objects.get(id=request.POST.get("category")),
            price=request.POST.get("price"),
            unit=request.POST.get("unit"),
            stock_quantity=request.POST.get("stock_quantity"),
            description=request.POST.get("description"),
            photo=request.FILES.get("photo"),
        )
        messages.success(request, "Material added.")
        return redirect('/viewmaterial/')
    return render(request, "material.html", {
        'suppliers': supplier.objects.all(),
        'categories': materialcategory.objects.all(),
    })

def material_suggestions(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'suggestions': []})
        
    results = material.objects.filter(
        Q(material_name__icontains=q) |
        Q(material_code__icontains=q) |
        Q(category__category_name__icontains=q)
    ).values('id', 'material_name', 'material_code', 'category__category_name')[:8]
    
    suggestions = []
    for r in results:
        suggestions.append({
            'id': r['id'],
            'name': r['material_name'],
            'code': r['material_code'] or '',
            'category': r['category__category_name']
        })
        
    return JsonResponse({'suggestions': suggestions})


def viewmaterial(request):
    if not check_login(request):
        return redirect('/insertlogin/')
        
    q = request.GET.get('q', '')
    data = material.objects.all().order_by('-id')
    
    if q:
        data = data.filter(
            Q(material_name__icontains=q) |
            Q(material_code__icontains=q) |
            Q(category__category_name__icontains=q)
        )
        
    return render(request, "showmaterial.html", {'data': data, 'q': q})


def material_detail(request, pk):
    if not check_login(request):
        return redirect('/insertlogin/')
    mat = get_object_or_404(material, pk=pk)
    return render(request, "material_detail.html", {'mat': mat})


def delmaterial(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    material.objects.get(pk=pk).delete()
    messages.success(request, "Material deleted.")
    return redirect('/viewmaterial/')


def editmaterial(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    data = get_object_or_404(material, pk=pk)
    if request.method == "POST":
        data.supplier = supplier.objects.get(id=request.POST.get("supplier"))
        data.category = materialcategory.objects.get(id=request.POST.get("category"))
        data.material_name = request.POST.get("material_name")
        data.material_code = request.POST.get("material_code")
        data.price = request.POST.get("price")
        data.unit = request.POST.get("unit")
        data.stock_quantity = request.POST.get("stock_quantity")
        data.description = request.POST.get("description")
        if request.FILES.get("photo"):
            data.photo = request.FILES.get("photo")
        data.save()
        messages.success(request, "Material updated.")
        return redirect('/viewmaterial/')
    return render(request, "editmaterial.html", {
        'x': data,
        'suppliers': supplier.objects.all(),
        'categories': materialcategory.objects.all(),
    })


# ============================================================
# PROJECT SITE
# ============================================================

def insertprojectsite(request):
    """Both admin and staff can add project sites.
    Staff submissions go to 'pending' approval; admin submissions are auto-approved."""
    if not check_login(request):
        return redirect('/insertlogin/')

    if request.method == "POST":
        user = get_current_user(request)
        user_is_admin = is_admin(request)

        # Staff: forced to planning + pending approval
        # Admin: uses selected status + auto-approved
        site_status = request.POST.get("status") if user_is_admin else "planning"
        approval = "approved" if user_is_admin else "pending"

        # Parse latitude/longitude from GPS capture
        lat = request.POST.get("latitude")
        lng = request.POST.get("longitude")
        lat = float(lat) if lat else None
        lng = float(lng) if lng else None

        new_site = projectsite.objects.create(
            manager=request.POST.get("manager"),
            site_name=request.POST.get("site_name"),
            location=request.POST.get("location"),
            latitude=lat,
            longitude=lng,
            project_type=request.POST.get("project_type"),
            start_date=request.POST.get("start_date"),
            expected_end_date=request.POST.get("expected_end_date"),
            status=site_status,
            created_by=user,
            approval_status=approval,
        )

        if user_is_admin:
            messages.success(request, "Project site added.")
        else:
            messages.success(request, "🏗️ Project site submitted for admin approval!")
            # Notify all admins
            for admin_user in userregistration.objects.filter(role='admin'):
                send_notification(
                    admin_user,
                    "🏗️ New Project Site Pending",
                    f"Staff '{user.name}' submitted project site '{new_site.site_name}' "
                    f"at {new_site.location}. Please review and approve."
                )
        return redirect('/viewprojectsite/')

    return render(request, "projectsite.html", {
        'users': [get_current_user(request)] if get_current_user(request) else [],
        'total_projects': projectsite.objects.count(),
        'active_projects': projectsite.objects.filter(status='active').count(),
        'is_admin': is_admin(request),
    })


def viewprojectsite(request):
    """Admin sees all sites; staff sees approved sites + their own pending/rejected."""
    if not check_login(request):
        return redirect('/insertlogin/')

    user = get_current_user(request)
    user_is_admin = is_admin(request)

    if user_is_admin:
        projects = projectsite.objects.all().order_by('-id')
    else:
        # Staff sees: only their own sites
        projects = projectsite.objects.filter(created_by=user).order_by('-id')

    # Optional filters from query string
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    approval_filter = request.GET.get('approval', '')

    if q:
        projects = projects.filter(
            Q(site_name__icontains=q) | Q(location__icontains=q)
        )
    if status_filter:
        projects = projects.filter(status=status_filter)
    if approval_filter and user_is_admin:
        projects = projects.filter(approval_status=approval_filter)

    # Count stats
    all_projects = projectsite.objects.all() if user_is_admin else projects
    pending_count = projectsite.objects.filter(approval_status='pending').count() if user_is_admin else 0

    return render(request, "showprojectsite.html", {
        'projects': projects,
        'is_admin': user_is_admin,
        'current_user': user,
        'pending_count': pending_count,
        'q': q,
        'status_filter': status_filter,
        'approval_filter': approval_filter,
    })


def delprojectsite(request, pk):
    """Admin only — delete any project site."""
    if admin_required(request):
        return redirect('/dashboard/')
    projectsite.objects.get(pk=pk).delete()
    messages.success(request, "Project site deleted.")
    return redirect('/viewprojectsite/')


def editprojectsite(request, pk):
    """Admin can edit any site. Staff can edit only their own pending sites."""
    if not check_login(request):
        return redirect('/insertlogin/')

    data = get_object_or_404(projectsite, pk=pk)
    user = get_current_user(request)
    user_is_admin = is_admin(request)

    # Staff can only edit their own pending sites
    if not user_is_admin:
        if data.created_by != user or data.approval_status != 'pending':
            messages.error(request, "⛔ You can only edit your own pending project sites.")
            return redirect('/viewprojectsite/')

    if request.method == "POST":
        data.manager = request.POST.get("manager")
        data.site_name = request.POST.get("site_name")
        data.location = request.POST.get("location")

        lat = request.POST.get("latitude")
        lng = request.POST.get("longitude")
        data.latitude = float(lat) if lat else data.latitude
        data.longitude = float(lng) if lng else data.longitude

        data.project_type = request.POST.get("project_type")
        data.start_date = request.POST.get("start_date")
        data.expected_end_date = request.POST.get("expected_end_date")

        # Staff cannot change status or approval
        if user_is_admin:
            data.status = request.POST.get("status")

        data.save()
        messages.success(request, "Project site updated.")
        return redirect('/viewprojectsite/')

    return render(request, "editprojectsite.html", {
        'x': data,
        'users': [user] if user else [],
        'is_admin': user_is_admin,
    })


def approve_projectsite(request, pk):
    """Admin approves a pending project site."""
    if admin_required(request):
        return redirect('/dashboard/')

    site = get_object_or_404(projectsite, pk=pk)
    site.approval_status = 'approved'
    site.save()

    # Notify the staff member who submitted it
    if site.created_by:
        send_notification(
            site.created_by,
            "✅ Project Site Approved",
            f"Your project site '{site.site_name}' has been approved by admin. "
            f"It is now available for orders and inventory."
        )

    messages.success(request, f"✅ '{site.site_name}' has been approved.")
    return redirect('/viewprojectsite/')


def reject_projectsite(request, pk):
    """Admin rejects a pending project site."""
    if admin_required(request):
        return redirect('/dashboard/')

    site = get_object_or_404(projectsite, pk=pk)
    site.approval_status = 'rejected'
    site.save()

    # Notify the staff member
    if site.created_by:
        send_notification(
            site.created_by,
            "❌ Project Site Rejected",
            f"Your project site '{site.site_name}' was not approved. "
            f"Please contact admin for details or re-submit with corrections."
        )

    messages.success(request, f"❌ '{site.site_name}' has been rejected.")
    return redirect('/viewprojectsite/')


# ============================================================
# ==================  AMAZON-STYLE FLOW  =====================
# ============================================================
#
#  STEP 1:  User adds materials to CART
#  STEP 2:  User goes to CHECKOUT → selects project site
#  STEP 3:  On confirm → ORDER is created automatically
#              └─ ORDER ITEMS are created for each cart item
#              └─ PAYMENT record is created (status=pending)
#              └─ INVENTORY is updated
#              └─ STOCK QUANTITY on material is reduced
#              └─ NOTIFICATION is sent to user
#              └─ CART is cleared
#  STEP 4:  Admin updates ORDER STATUS (processing → shipped → delivered)
#              └─ On 'delivered' → PAYMENT status becomes 'paid'
#              └─ DELIVERY record is created automatically
#
# ============================================================


# -----------------------------------------------------------
# CART: ADD TO CART
# -----------------------------------------------------------

def add_to_cart(request, material_id):
    """
    Add a material to cart or increase quantity if already added.
    Like Amazon's 'Add to Cart' button.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    user = get_current_user(request)

    # Prevent staff without at least 1 project site from ordering/adding to cart
    if not is_admin(request):
        site_count = projectsite.objects.filter(created_by=user).count()
        if site_count == 0:
            messages.error(request, "⚠️ You must add at least 1 project site before you can order materials.")
            return redirect('/insertprojectsite/')

    mat = get_object_or_404(material, id=material_id)

    if mat.stock_quantity is None or mat.stock_quantity <= 0:
        messages.error(request, f"'{mat.material_name}' is out of stock.")
        return redirect('/viewmaterial/')

    # Support qty from POST if available
    qty_to_add = 1
    if request.method == 'POST':
        try:
            qty_to_add = int(request.POST.get('qty', 1))
        except ValueError:
            qty_to_add = 1
            
    if qty_to_add < 1:
        qty_to_add = 1

    cart_item, created = cart.objects.get_or_create(user=user, material=mat)

    if created:
        cart_item.quantity = min(qty_to_add, mat.stock_quantity)
        cart_item.save()
        messages.success(request, f"'{mat.material_name}' added to cart!")
    else:
        new_qty = cart_item.quantity + qty_to_add
        if new_qty <= mat.stock_quantity:
            cart_item.quantity = new_qty
            cart_item.save()
            messages.success(request, f"Quantity updated in cart.")
        else:
            cart_item.quantity = mat.stock_quantity
            cart_item.save()
            messages.warning(request, f"Cannot add more — only {mat.stock_quantity} in stock. Maxed out in cart.")

    return redirect('/viewcart/')


# -----------------------------------------------------------
# BUY NOW: SKIP CART → GO DIRECTLY TO CHECKOUT
# -----------------------------------------------------------

def buy_now(request, material_id):
    """
    Like Amazon's 'Buy Now' — clears cart, adds this item,
    and redirects straight to checkout.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    user = get_current_user(request)

    # Prevent staff without at least 1 project site from ordering
    if not is_admin(request):
        site_count = projectsite.objects.filter(created_by=user).count()
        if site_count == 0:
            messages.error(request, "⚠️ You must add at least 1 project site before you can order materials.")
            return redirect('/insertprojectsite/')

    mat = get_object_or_404(material, id=material_id)

    if mat.stock_quantity is None or mat.stock_quantity <= 0:
        messages.error(request, f"'{mat.material_name}' is out of stock.")
        return redirect('/viewmaterial/')

    # Support qty from POST if available
    qty_to_buy = 1
    if request.method == 'POST':
        try:
            qty_to_buy = int(request.POST.get('qty', 1))
        except ValueError:
            qty_to_buy = 1
            
    if qty_to_buy < 1:
        qty_to_buy = 1
        
    qty_to_buy = min(qty_to_buy, mat.stock_quantity)

    # Clear existing cart and add only this item
    cart.objects.filter(user=user).delete()
    cart.objects.create(user=user, material=mat, quantity=qty_to_buy)

    return redirect('/checkout/')


# -----------------------------------------------------------
# CART: VIEW CART
# -----------------------------------------------------------


def viewcart(request):
    """
    Show all cart items with subtotals and grand total.
    Like Amazon's cart page.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    user = get_current_user(request)

    # Prevent staff without at least 1 project site from ordering/viewing cart
    if not is_admin(request):
        site_count = projectsite.objects.filter(created_by=user).count()
        if site_count == 0:
            messages.error(request, "⚠️ You must add at least 1 project site before you can order materials.")
            return redirect('/insertprojectsite/')

    cart_items = cart.objects.filter(user=user).select_related('material')
    grand_total = sum(item.get_subtotal() for item in cart_items)

    return render(request, "cart.html", {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })


# -----------------------------------------------------------
# CART: UPDATE QUANTITY
# -----------------------------------------------------------

def update_cart(request, cart_id):
    if not check_login(request):
        return redirect('/insertlogin/')

    cart_item = get_object_or_404(cart, id=cart_id)
    action = request.POST.get("action")  # 'increase' or 'decrease' or 'remove'

    if action == "increase":
        if cart_item.quantity < cart_item.material.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, "Max stock reached.")
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == "remove":
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect('/viewcart/')


# -----------------------------------------------------------
# CHECKOUT: SELECT PROJECT SITE + PAYMENT METHOD
# -----------------------------------------------------------

def checkout(request):
    """
    Checkout page — user picks project site, supplier, payment method.
    Like Amazon's 'Proceed to Buy' page.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    user = get_current_user(request)

    # Prevent staff without at least 1 project site from checking out
    if not is_admin(request):
        site_count = projectsite.objects.filter(created_by=user).count()
        if site_count == 0:
            messages.error(request, "⚠️ You must add at least 1 project site before you can order materials.")
            return redirect('/insertprojectsite/')

    cart_items = cart.objects.filter(user=user).select_related('material', 'material__supplier')

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('/viewmaterial/')

    grand_total = sum(item.get_subtotal() for item in cart_items)

    # Group items by supplier
    supplier_totals = {}
    for item in cart_items:
        sup = item.material.supplier
        if sup.id not in supplier_totals:
            supplier_totals[sup.id] = {'supplier': sup, 'total': 0}
        supplier_totals[sup.id]['total'] += float(item.get_subtotal())

    user_is_admin = is_admin(request)

    if user_is_admin:
        projects = projectsite.objects.filter(approval_status='approved')
    else:
        projects = projectsite.objects.filter(approval_status='approved', created_by=user)

    return render(request, "checkout.html", {
        'cart_items': cart_items,
        'grand_total': grand_total,
        'supplier_totals': supplier_totals.values(),
        'projects': projects,
    })


# -----------------------------------------------------------
# PLACE ORDER: THE CORE AUTO FLOW
# -----------------------------------------------------------

def place_order(request):
    """
    ★ MAIN AUTO FLOW — runs when user clicks 'Confirm Order'

    For UPI/Bank: redirects to payment processing page first.
    For COD/Razorpay: places order directly.

    Automatically:
      1. Creates materialorder
      2. Creates orderitem for each cart item
      3. Reduces material stock_quantity
      4. Creates payment record (status=pending)
      5. Sends notification to user
      6. Clears the cart
      NOTE: Inventory is updated only after successful delivery.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    if request.method != "POST":
        return redirect('/checkout/')

    user = get_current_user(request)
    cart_items = cart.objects.filter(user=user).select_related('material', 'material__supplier')

    if not cart_items.exists():
        messages.error(request, "Cart is empty.")
        return redirect('/viewmaterial/')

    # ── GET FORM DATA ──────────────────────────────────────
    project_id = request.POST.get("project_site")
    payment_method_val = request.POST.get("payment_method", "cod")
    delivery_days = int(request.POST.get("delivery_days", 5))

    # ── FOR UPI / BANK: Redirect to payment processing page ──
    if payment_method_val in ('upi', 'bank'):
        grand_total = sum(item.get_subtotal() for item in cart_items)
        txn_preview = str(random.randint(10000000, 99999999))
        context = {
            'payment_method': payment_method_val,
            'grand_total': grand_total,
            'project_site': project_id,
            'delivery_days': delivery_days,
            'txn_preview': txn_preview,
            # UPI fields
            'upi_id': request.POST.get("upi_id", ""),
            # Bank fields
            'bank_holder': request.POST.get("bank_holder", ""),
            'bank_name': request.POST.get("bank_name", ""),
            'bank_account': request.POST.get("bank_account", ""),
            'bank_ifsc': request.POST.get("bank_ifsc", ""),
        }
        return render(request, "payment_processing.html", context)

    # ── FOR COD / RAZORPAY: Place order directly ──────────
    return _execute_place_order(request, user, cart_items, project_id, payment_method_val, delivery_days)


def confirm_payment(request):
    """
    Called after UPI/Bank payment processing page verifies the payment.
    Actually places the order using the same logic as COD/Razorpay.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    if request.method != "POST":
        return redirect('/checkout/')

    user = get_current_user(request)
    cart_items = cart.objects.filter(user=user).select_related('material', 'material__supplier')

    if not cart_items.exists():
        messages.error(request, "Cart is empty.")
        return redirect('/viewmaterial/')

    project_id = request.POST.get("project_site")
    payment_method_val = request.POST.get("payment_method", "upi")
    delivery_days = int(request.POST.get("delivery_days", 5))

    return _execute_place_order(request, user, cart_items, project_id, payment_method_val, delivery_days, paid=True)


def _execute_place_order(request, user, cart_items, project_id, payment_method_val, delivery_days, paid=False):
    """
    Internal helper that actually creates orders, items, payments, etc.
    If paid=True (UPI/Bank verified), payment status is set to 'paid' immediately.
    """
    project_obj = get_object_or_404(projectsite, id=project_id)

    # ── GROUP CART ITEMS BY SUPPLIER ──────────────────────
    supplier_map = {}
    for item in cart_items:
        sup_id = item.material.supplier.id
        if sup_id not in supplier_map:
            supplier_map[sup_id] = {
                'supplier': item.material.supplier,
                'items': []
            }
        supplier_map[sup_id]['items'].append(item)

    placed_orders = []

    for sup_id, data in supplier_map.items():

        sup = data['supplier']
        items = data['items']
        total = sum(item.get_subtotal() for item in items)
        tracking = "MO" + str(random.randint(100000, 999999))
        exp_date = date.today() + timedelta(days=delivery_days)

        pay_status = 'paid' if paid else 'pending'

        # ── STEP 1: CREATE ORDER ───────────────────────────
        order_obj = materialorder.objects.create(
            project_site=project_obj,
            ordered_by=user,
            supplier=sup,
            total_amount=total,
            tracking_id=tracking,
            order_status='placed',
            payment_status=pay_status,
            expected_delivery_date=exp_date,
        )

        # ── STEP 2: CREATE ORDER ITEMS ─────────────────────
        for item in items:
            orderitem.objects.create(
                order=order_obj,
                material=item.material,
                quantity=item.quantity,
                unit_price=item.material.price,
            )

            # ── STEP 3: REDUCE MATERIAL STOCK ─────────────
            mat = item.material
            if mat.stock_quantity is not None:
                mat.stock_quantity = max(0, mat.stock_quantity - item.quantity)
                mat.save()

                if mat.stock_quantity <= 10:
                    send_notification(
                        user,
                        "⚠️ Low Stock Alert",
                        f"'{mat.material_name}' is running low — only {mat.stock_quantity} left."
                    )

            # ── NOTE: Inventory updates on delivery, not on order placement ──

        # ── STEP 5: CREATE PAYMENT RECORD ──────────────────
        txn_id = "TXN" + str(random.randint(10000000, 99999999))
        payment.objects.create(
            order=order_obj,
            supplier=sup,
            amount=total,
            payment_method=payment_method_val,
            transaction_id=txn_id,
            status=pay_status,
        )

        # ── STEP 6: SEND NOTIFICATION ──────────────────────
        pay_label = "UPI" if payment_method_val == 'upi' else "Bank Transfer" if payment_method_val == 'bank' else payment_method_val.upper()
        status_msg = f"Payment of ₹{total} received via {pay_label}. " if paid else ""
        send_notification(
            user,
            "✅ Order Placed Successfully",
            f"Order #{order_obj.id} placed with {sup.company_name}. "
            f"Tracking ID: {tracking}. {status_msg}"
            f"Expected delivery by {exp_date}."
        )

        placed_orders.append(order_obj)

    # ── STEP 7: CLEAR CART ─────────────────────────────────
    cart.objects.filter(user=user).delete()

    if paid:
        messages.success(request, f"💳 Payment verified! {len(placed_orders)} order(s) placed successfully!")
    else:
        messages.success(request, f"🎉 {len(placed_orders)} order(s) placed successfully!")
    return redirect('/viewmaterialorder/')


# -----------------------------------------------------------
# ORDER STATUS UPDATE (Admin updates: processing → delivered)
# -----------------------------------------------------------

def update_order_status(request, pk):
    """
    ADMIN ONLY — When admin marks order as 'delivered':
      - Payment status automatically becomes 'paid'
      - Delivery record is auto-created
    """
    if admin_required(request):
        return redirect('/dashboard/')

    order_obj = get_object_or_404(materialorder, pk=pk)
    new_status = request.POST.get("order_status")

    order_obj.order_status = new_status
    order_obj.save()

    # ── AUTO: Mark payment as paid when delivered ──────────
    if new_status == 'delivered':
        try:
            pay = payment.objects.get(order=order_obj)
            pay.status = 'paid'
            pay.save()
            order_obj.payment_status = 'paid'
            order_obj.save()
        except payment.DoesNotExist:
            pass

        # ── AUTO: Create delivery record ───────────────────
        delivery.objects.get_or_create(
            order=order_obj,
            defaults={
                'received_by': order_obj.ordered_by,
                'delivery_date': date.today(),
                'delivery_status': 'delivered',
                'delivery_note': 'Auto-confirmed on delivery',
            }
        )

        # ── AUTO: Update inventory at project site on delivery ──
        order_items = orderitem.objects.filter(order=order_obj)
        for oi in order_items:
            inv, created = inventory.objects.get_or_create(
                project_site=order_obj.project_site,
                material=oi.material,
                defaults={'available_quantity': oi.quantity, 'used_quantity': 0}
            )
            if not created:
                inv.available_quantity += oi.quantity
                inv.save()

        # ── NOTIFY USER ────────────────────────────────────
        send_notification(
            order_obj.ordered_by,
            "📦 Order Delivered!",
            f"Order #{order_obj.id} has been delivered. "
            f"Payment of ₹{order_obj.total_amount} confirmed."
        )

    # ── AUTO: Reverse inventory & stock when cancelled ─────
    if new_status == 'cancelled':
        order_items = orderitem.objects.filter(order=order_obj)
        for oi in order_items:
            # Restore material stock
            mat = oi.material
            if mat.stock_quantity is not None:
                mat.stock_quantity += oi.quantity
                mat.save()

            # NOTE: No inventory reversal needed — inventory is only added on delivery

        # Auto-refund payment
        try:
            pay = payment.objects.get(order=order_obj)
            pay.status = 'refunded'
            pay.save()
            order_obj.payment_status = 'refunded'
            order_obj.save()
        except payment.DoesNotExist:
            pass

        # Notify user
        send_notification(
            order_obj.ordered_by,
            "❌ Order Cancelled",
            f"Order #{order_obj.id} has been cancelled. "
            f"₹{order_obj.total_amount} will be refunded. "
            f"Stock has been restored automatically."
        )

    messages.success(request, f"Order status updated to '{new_status}'.")
    return redirect('/viewmaterialorder/')


# -----------------------------------------------------------
# ORDER VIEWS (standard CRUD)
# -----------------------------------------------------------

def viewmaterialorder(request):
    if not check_login(request):
        return redirect('/insertlogin/')

    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    data = materialorder.objects.all().prefetch_related(
        'items', 'items__material'
    ).select_related(
        'project_site', 'supplier', 'ordered_by'
    ).order_by('-id')

    if q:
        data = data.filter(
            Q(project_site__site_name__icontains=q) |
            Q(supplier__company_name__icontains=q) |
            Q(tracking_id__icontains=q) |
            Q(id__icontains=q)
        )
    if status:
        data = data.filter(order_status=status)

    # Staff sees only their own orders; admin sees all
    if not is_admin(request):
        user = get_current_user(request)
        if user:
            data = data.filter(ordered_by=user)

    return render(request, "showmaterialorder.html", {
        'data': data,
        'q': q,
        'status': status,
        'is_admin': is_admin(request),
    })


def delmaterialorder(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    materialorder.objects.get(pk=pk).delete()
    messages.success(request, "Order deleted.")
    return redirect('/viewmaterialorder/')


def order_detail(request, pk):
    """Show full order with all items — like Amazon order detail page"""
    if not check_login(request):
        return redirect('/insertlogin/')
    order_obj = get_object_or_404(materialorder, pk=pk)
    items = orderitem.objects.filter(order=order_obj)
    pay = payment.objects.filter(order=order_obj).first()
    dlv = delivery.objects.filter(order=order_obj).first()
    return render(request, "orderdetail.html", {
        'order': order_obj,
        'items': items,
        'pay': pay,
        'dlv': dlv,
    })


# -----------------------------------------------------------
# ORDER ITEM VIEWS (for manual use / admin only)
# -----------------------------------------------------------

def vieworderitem(request):
    if not check_login(request):
        return redirect('/insertlogin/')
    items = orderitem.objects.all()
    grand_total = sum(float(i.subtotal) for i in items)
    return render(request, "showorderitem.html", {'items': items, 'grand_total': grand_total})


def delorderitem(request, pk):
    orderitem.objects.get(pk=pk).delete()
    messages.success(request, "Order item deleted.")
    return redirect('/vieworderitem/')


# ============================================================
# DELIVERY
# ============================================================

def insertdelivery(request):
    if admin_required(request):
        return redirect('/dashboard/')
    orders = materialorder.objects.all()
    users = userregistration.objects.all()
    if request.method == "POST":
        order_obj = materialorder.objects.get(id=request.POST.get("order"))
        user_id = request.POST.get("received_by")
        user_obj = userregistration.objects.get(id=user_id) if user_id else None

        delivery.objects.create(
            order=order_obj,
            received_by=user_obj,
            delivery_date=request.POST.get("delivery_date"),
            delivery_status=request.POST.get("delivery_status"),
            delivery_note=request.POST.get("delivery_note"),
            photo=request.FILES.get("photo"),
        )
        messages.success(request, "Delivery added.")
        return redirect('/viewdelivery/')
    return render(request, "delivery.html", {'orders': orders, 'users': users})


def viewdelivery(request):
    if not check_login(request):
        return redirect('/insertlogin/')
        
    data = delivery.objects.all().order_by('-id')
    if not is_admin(request):
        user = get_current_user(request)
        if user:
            data = data.filter(order__ordered_by=user)
            
    return render(request, "showdelivery.html", {'deliveries': data})


def editdelivery(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    data = get_object_or_404(delivery, pk=pk)
    orders = materialorder.objects.all()
    users = userregistration.objects.all()
    if request.method == "POST":
        data.order = materialorder.objects.get(id=request.POST.get("order"))
        
        user_id = request.POST.get("received_by")
        data.received_by = userregistration.objects.get(id=user_id) if user_id else None
        
        data.delivery_date = request.POST.get("delivery_date")
        data.delivery_status = request.POST.get("delivery_status")
        data.delivery_note = request.POST.get("delivery_note")
        if request.FILES.get("photo"):
            data.photo = request.FILES.get("photo")
        data.save()
        messages.success(request, "Delivery updated.")
        return redirect('/viewdelivery/')
    return render(request, "editdelivery.html", {'x': data, 'orders': orders, 'users': users})


def deldelivery(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    delivery.objects.get(pk=pk).delete()
    messages.success(request, "Delivery deleted.")
    return redirect('/viewdelivery/')


# ============================================================
# INVENTORY
# ============================================================

def insertinventory(request):
    if admin_required(request):
        return redirect('/dashboard/')
    if request.method == "POST":
        inventory.objects.create(
            project_site=projectsite.objects.get(id=request.POST.get("project_site")),
            material=material.objects.get(id=request.POST.get("material")),
            available_quantity=request.POST.get("available_quantity"),
            used_quantity=request.POST.get("used_quantity"),
        )
        messages.success(request, "Inventory added.")
        return redirect('/viewinventory/')
    return render(request, "inventory.html", {
        'projects': projectsite.objects.filter(approval_status='approved'),
        'materials': material.objects.all(),
    })


def viewinventory(request):
    if not check_login(request):
        return redirect('/insertlogin/')

    data = inventory.objects.all().select_related('project_site', 'material')
    if not is_admin(request):
        user = get_current_user(request)
        if user:
            data = data.filter(project_site__created_by=user)

    total_items = data.count()
    total_available = sum(i.available_quantity for i in data)
    low_stock = data.filter(available_quantity__gt=0, available_quantity__lte=10).count()
    out_of_stock = data.filter(available_quantity=0).count()

    return render(request, "showinventory.html", {
        'data': data,
        'total_items': total_items,
        'total_available': total_available,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    })


def delinventory(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    inventory.objects.get(pk=pk).delete()
    messages.success(request, "Inventory deleted.")
    return redirect('/viewinventory/')


def editinventory(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    data = get_object_or_404(inventory, pk=pk)
    if request.method == "POST":
        data.project_site = projectsite.objects.get(id=request.POST.get("project_site"))
        data.material = material.objects.get(id=request.POST.get("material"))
        data.available_quantity = request.POST.get("available_quantity")
        data.used_quantity = request.POST.get("used_quantity")
        data.save()
        messages.success(request, "Inventory updated.")
        return redirect('/viewinventory/')
    return render(request, "editinventory.html", {
        'x': data,
        'projects': projectsite.objects.filter(approval_status='approved'),
        'materials': material.objects.all(),
    })


# ============================================================
# PAYMENT
# ============================================================

def viewpayment(request):
    if not check_login(request):
        return redirect('/insertlogin/')
        
    data = payment.objects.all().order_by('-id')
    if not is_admin(request):
        user = get_current_user(request)
        if user:
            data = data.filter(order__ordered_by=user)
            
    return render(request, "showpayment.html", {'data': data})


def delpayment(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    payment.objects.get(pk=pk).delete()
    messages.success(request, "Payment deleted.")
    return redirect('/viewpayment/')


# ============================================================
# REVIEW
# ============================================================

def insertreview(request):
    if not check_login(request):
        return redirect('/insertlogin/')
    if request.method == "POST":
        user = get_current_user(request)
        review.objects.create(
            reviewer=user,
            supplier=supplier.objects.get(id=request.POST.get("supplier")),
            material=material.objects.get(id=request.POST.get("material")),
            rating=request.POST.get("rating"),
            comments=request.POST.get("comments"),
        )
        messages.success(request, "Review submitted.")
        return redirect('/viewreview/')
    return render(request, "review.html", {
        'suppliers': supplier.objects.all(),
        'materials': material.objects.all(),
    })


def viewreview(request):
    if not check_login(request):
        return redirect('/insertlogin/')
    return render(request, "showreview.html", {'data': review.objects.all()})


def delreview(request, pk):
    review.objects.get(pk=pk).delete()
    messages.success(request, "Review deleted.")
    return redirect('/viewreview/')


# ============================================================
# NOTIFICATION
# ============================================================

def viewnotification(request):
    if not check_login(request):
        return redirect('/insertlogin/')
    user = get_current_user(request)
    notifs = notification.objects.filter(user=user).order_by('-notification_date')
    # Mark all as read
    notifs.update(is_read=True)
    return render(request, "shownotification.html", {'data': notifs})


def cancel_order(request, pk):
    """
    ANY logged-in user can cancel their OWN order,
    but ONLY when the status is 'placed' or 'processing'.
    Reuses the same reversal logic as admin's update_order_status.
    """
    if not check_login(request):
        return redirect('/insertlogin/')

    order_obj = get_object_or_404(materialorder, pk=pk)
    user = get_current_user(request)

    # Ensure the user owns this order (or is admin)
    if order_obj.ordered_by != user and not is_admin(request):
        messages.error(request, "⛔ You can only cancel your own orders.")
        return redirect('/viewmaterialorder/')

    # Only allow cancellation for early-stage orders
    if order_obj.order_status not in ('placed', 'processing'):
        messages.error(request, "❌ This order can no longer be cancelled — it has already been shipped or delivered.")
        return redirect(f'/order_detail/{order_obj.id}/')

    # ── CANCEL: Reverse stock, inventory & payment ──────────
    order_obj.order_status = 'cancelled'
    order_obj.save()

    order_items = orderitem.objects.filter(order=order_obj)
    for oi in order_items:
        # Restore material stock
        mat = oi.material
        if mat.stock_quantity is not None:
            mat.stock_quantity += oi.quantity
            mat.save()

        # NOTE: No inventory reversal needed — inventory is only added on delivery

    # Auto-refund payment
    try:
        pay = payment.objects.get(order=order_obj)
        pay.status = 'refunded'
        pay.save()
        order_obj.payment_status = 'refunded'
        order_obj.save()
    except payment.DoesNotExist:
        pass

    # Notify user
    send_notification(
        order_obj.ordered_by,
        "❌ Order Cancelled",
        f"Order #{order_obj.id} has been cancelled by you. "
        f"₹{order_obj.total_amount} will be refunded. "
        f"Stock has been restored automatically."
    )

    messages.success(request, f"Order #{order_obj.id} has been cancelled successfully. Refund initiated.")
    return redirect('/viewmaterialorder/')


def delnotification(request, pk):
    if admin_required(request):
        return redirect('/dashboard/')
    notification.objects.get(pk=pk).delete()
    messages.success(request, "Notification deleted.")
    return redirect('/viewnotification/')
