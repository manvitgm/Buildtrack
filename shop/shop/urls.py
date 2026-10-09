"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from customer import views

urlpatterns = [

    # ADMIN
    path('admin/', admin.site.urls),

    # HOME
    path('', views.frontpage, name='frontpage'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # LOGIN / LOGOUT
    path('insertlogin/',          views.insertlogin,          name='insertlogin'),
    path('logout/',               views.logout,               name='logout'),
    path('refresh_captcha/',      views.refresh_captcha,      name='refresh_captcha'),

    # FORGOT PASSWORD & OTP
    path('forgot_password/',      views.forgot_password,      name='forgot_password'),
    path('verify_otp/',           views.verify_otp,           name='verify_otp'),
    path('reset_password/',       views.reset_password,       name='reset_password'),

    # USER REGISTRATION
    path('insertuserregistration/', views.insertuserregistration, name='insertuserregistration'),
    path('viewuserregistration/',   views.viewuserregistration,   name='viewuserregistration'),
    path('delusereg/<int:pk>/',     views.delusereg,              name='delusereg'),

    # SUPPLIER
    path('insertsupplier/',          views.insertsupplier,   name='insertsupplier'),
    path('viewsupplier/',            views.viewsupplier,     name='viewsupplier'),
    path('editsupplier/<int:pk>/',   views.editsupplier,     name='editsupplier'),
    path('delsupp/<int:pk>/',        views.delsupp,          name='delsupp'),

    # MATERIAL CATEGORY
    path('insertmaterialcategory/',          views.insertmaterialcategory, name='insertmaterialcategory'),
    path('viewmaterialcategory/',            views.viewmaterialcategory,   name='viewmaterialcategory'),
    path('editmaterialcategory/<int:pk>/',   views.editmaterialcategory,   name='editmaterialcategory'),
    path('delmaterialcategory/<int:pk>/',    views.delmaterialcategory,    name='delmaterialcategory'),

    # MATERIAL
    path('insertmaterial/',        views.insertmaterial, name='insertmaterial'),
    path('viewmaterial/',          views.viewmaterial,   name='viewmaterial'),
    path('material_suggestions/',  views.material_suggestions, name='material_suggestions'),
    path('material_detail/<int:pk>/', views.material_detail, name='material_detail'),
    path('editmaterial/<int:pk>/', views.editmaterial,   name='editmaterial'),
    path('delmaterial/<int:pk>/',  views.delmaterial,    name='delmaterial'),

    # PROJECT SITE
    path('insertprojectsite/',          views.insertprojectsite, name='insertprojectsite'),
    path('viewprojectsite/',            views.viewprojectsite,   name='viewprojectsite'),
    path('editprojectsite/<int:pk>/',   views.editprojectsite,   name='editprojectsite'),
    path('delprojectsite/<int:pk>/',    views.delprojectsite,    name='delprojectsite'),
    path('approveprojectsite/<int:pk>/', views.approve_projectsite, name='approveprojectsite'),
    path('rejectprojectsite/<int:pk>/',  views.reject_projectsite,  name='rejectprojectsite'),

    # ─────────────────────────────────────────────────────
    #  AMAZON-STYLE FLOW  (NEW)
    # ─────────────────────────────────────────────────────

    # CART
    path('add_to_cart/<int:material_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy_now/<int:material_id>/',     views.buy_now,     name='buy_now'),
    path('viewcart/',                      views.viewcart,     name='viewcart'),
    path('update_cart/<int:cart_id>/',     views.update_cart,  name='update_cart'),

    # CHECKOUT → PLACE ORDER
    path('checkout/',         views.checkout,         name='checkout'),
    path('place_order/',      views.place_order,      name='place_order'),
    path('confirm_payment/',  views.confirm_payment,  name='confirm_payment'),

    # ORDER MANAGEMENT
    path('viewmaterialorder/',                        views.viewmaterialorder,    name='viewmaterialorder'),
    path('order_detail/<int:pk>/',                    views.order_detail,         name='order_detail'),
    path('delmaterialorder/<int:pk>/',                views.delmaterialorder,     name='delmaterialorder'),
    path('update_order_status/<int:pk>/',             views.update_order_status,  name='update_order_status'),
    path('cancel_order/<int:pk>/',                     views.cancel_order,         name='cancel_order'),

    # ORDER ITEMS (admin view)
    path('vieworderitem/',             views.vieworderitem, name='vieworderitem'),
    path('delorderitem/<int:pk>/',     views.delorderitem,  name='delorderitem'),

    # ─────────────────────────────────────────────────────

    # DELIVERY
    path('insertdelivery/',          views.insertdelivery, name='insertdelivery'),
    path('viewdelivery/',            views.viewdelivery,   name='viewdelivery'),
    path('editdelivery/<int:pk>/',   views.editdelivery,   name='editdelivery'),
    path('deldelivery/<int:pk>/',    views.deldelivery,    name='deldelivery'),

    # INVENTORY
    path('insertinventory/',         views.insertinventory, name='insertinventory'),
    path('viewinventory/',           views.viewinventory,   name='viewinventory'),
    path('editinventory/<int:pk>/',  views.editinventory,   name='editinventory'),
    path('delinventory/<int:pk>/',   views.delinventory,    name='delinventory'),

    # PAYMENT (auto-created — view only)
    path('viewpayment/',           views.viewpayment, name='viewpayment'),
    path('delpayment/<int:pk>/',   views.delpayment,  name='delpayment'),

    # REVIEW
    path('insertreview/',        views.insertreview, name='insertreview'),
    path('viewreview/',          views.viewreview,   name='viewreview'),
    path('delreview/<int:pk>/',  views.delreview,    name='delreview'),

    # NOTIFICATION
    path('viewnotification/',          views.viewnotification, name='viewnotification'),
    path('delnotification/<int:pk>/',  views.delnotification,  name='delnotification'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)