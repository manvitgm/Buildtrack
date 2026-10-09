from django.db import models
from django.utils import timezone


# ============================================================
# 1. USER REGISTRATION
# ============================================================
class userregistration(models.Model):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )

    name     = models.CharField(max_length=100)
    email    = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    contact  = models.CharField(max_length=20)
    city     = models.CharField(max_length=100)
    role     = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    staff_role = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


# ============================================================
# 2. SUPPLIER
# ============================================================
class supplier(models.Model):

    user              = models.CharField(max_length=40)
    company_name      = models.CharField(max_length=100)
    gst_number        = models.CharField(max_length=30)
    specialization    = models.CharField(max_length=100)
    warehouse_address = models.CharField(max_length=200)
    rating            = models.CharField(max_length=10)
    logo              = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return self.company_name


# ============================================================
# 3. MATERIAL CATEGORY
# ============================================================
class materialcategory(models.Model):

    category_name   = models.CharField(max_length=50)
    description     = models.CharField(max_length=200)
    parent_category = models.CharField(max_length=40)

    def __str__(self):
        return self.category_name


# ============================================================
# 4. MATERIAL
# ============================================================
class material(models.Model):

    QUALITY_CHOICES = [
        ('good',    'Good'),
        ('average', 'Average'),
        ('poor',    'Poor'),
    ]

    category       = models.ForeignKey(materialcategory, on_delete=models.CASCADE)
    supplier       = models.ForeignKey(supplier,         on_delete=models.CASCADE)
    material_name  = models.CharField(max_length=100)
    material_code  = models.CharField(max_length=50,  blank=True, null=True)
    unit           = models.CharField(max_length=30)
    price          = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(null=True, blank=True)
    description    = models.TextField(blank=True, null=True)
    photo          = models.ImageField(upload_to='materials/', blank=True, null=True)
    quality_status = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='good')

    def __str__(self):
        return self.material_name


# ============================================================
# 5. PROJECT SITE
# ============================================================
class projectsite(models.Model):

    APPROVAL_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    manager             = models.CharField(max_length=100)
    site_name           = models.CharField(max_length=100)
    location            = models.CharField(max_length=200)
    latitude            = models.FloatField(null=True, blank=True)
    longitude           = models.FloatField(null=True, blank=True)
    project_type        = models.CharField(max_length=100)
    start_date          = models.CharField(max_length=50)
    expected_end_date   = models.CharField(max_length=50)
    status              = models.CharField(max_length=50)
    created_by          = models.ForeignKey(userregistration, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')
    approval_status     = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='approved')

    def __str__(self):
        return self.site_name


# ============================================================
# 6. CART  (NEW - like Amazon cart)
# ============================================================
class cart(models.Model):

    user         = models.ForeignKey(userregistration, on_delete=models.CASCADE)
    material     = models.ForeignKey(material,         on_delete=models.CASCADE)
    quantity     = models.IntegerField(default=1)
    added_date   = models.DateTimeField(auto_now_add=True)

    def get_subtotal(self):
        return self.quantity * (self.material.price or 0)

    def __str__(self):
        return f"{self.user.name} - {self.material.material_name}"


# ============================================================
# 7. MATERIAL ORDER
# ============================================================
class materialorder(models.Model):

    ORDER_STATUS_CHOICES = [
        ('placed',           'Placed'),
        ('processing',       'Processing'),
        ('shipped',          'Shipped'),
        ('out_for_delivery', 'Out For Delivery'),
        ('delivered',        'Delivered'),
        ('cancelled',        'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]

    project_site           = models.ForeignKey(projectsite, on_delete=models.CASCADE)
    ordered_by             = models.ForeignKey(userregistration, on_delete=models.CASCADE)
    supplier               = models.ForeignKey(supplier,     on_delete=models.CASCADE)
    order_date             = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    total_amount           = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tracking_id            = models.CharField(max_length=100, blank=True, null=True)
    order_status           = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='placed')
    payment_status         = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} - {self.project_site.site_name}"


# ============================================================
# 8. ORDER ITEM
# ============================================================
class orderitem(models.Model):

    order       = models.ForeignKey(materialorder, on_delete=models.CASCADE, related_name='items')
    material    = models.ForeignKey(material,      on_delete=models.CASCADE)
    quantity    = models.IntegerField()
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal    = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Auto-calculate subtotal on every save
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.material_name} x {self.quantity}"


# ============================================================
# 9. PAYMENT  (ForeignKey fixed - was CharField before)
# ============================================================
class payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('upi',      'UPI'),
        ('cod',      'Cash on Delivery'),
        ('bank',     'Bank Transfer'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]

    order          = models.OneToOneField(materialorder, on_delete=models.CASCADE)  # One order = one payment
    supplier       = models.ForeignKey(supplier,         on_delete=models.CASCADE)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date   = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='cod')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status         = models.CharField(max_length=20,  choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"


# ============================================================
# 10. DELIVERY  (ForeignKey fixed - was CharField before)
# ============================================================
class delivery(models.Model):

    order           = models.OneToOneField(materialorder,    on_delete=models.CASCADE)
    received_by     = models.ForeignKey(userregistration,    on_delete=models.SET_NULL, null=True, blank=True)
    delivery_date   = models.DateField(null=True, blank=True)
    delivery_status = models.CharField(max_length=20, default='pending')
    delivery_note   = models.CharField(max_length=200, blank=True)
    photo           = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"


# ============================================================
# 11. INVENTORY
# ============================================================
class inventory(models.Model):

    project_site       = models.ForeignKey(projectsite, on_delete=models.CASCADE)
    material           = models.ForeignKey(material,    on_delete=models.CASCADE)
    available_quantity = models.IntegerField(default=0)
    used_quantity      = models.IntegerField(default=0)
    last_updated       = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.material} at {self.project_site}"


# ============================================================
# 12. NOTIFICATION  (ForeignKey fixed - was CharField before)
# ============================================================
class notification(models.Model):

    user              = models.ForeignKey(userregistration, on_delete=models.CASCADE)
    title             = models.CharField(max_length=100)
    message           = models.CharField(max_length=300)
    notification_date = models.DateTimeField(auto_now_add=True)
    is_read           = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} -> {self.user.name}"


# ============================================================
# 13. REVIEW  (ForeignKey fixed - was CharField before)
# ============================================================
class review(models.Model):

    reviewer    = models.ForeignKey(userregistration, on_delete=models.CASCADE)
    supplier    = models.ForeignKey(supplier,         on_delete=models.CASCADE)
    material    = models.ForeignKey(material,         on_delete=models.CASCADE)
    rating      = models.IntegerField(default=5)
    comments    = models.TextField(blank=True)
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.name}"
