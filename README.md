# 🏗️ BuildTrack — Material Management System

A comprehensive web-based **Material Management System** built with Django for managing construction materials, suppliers, orders, inventory, and project sites — featuring an Amazon-style shopping cart and checkout flow.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Models](#-models)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)

---

## ✨ Features

### 🛒 Amazon-Style Shopping Flow
- **Browse Materials** — Search, filter, and view detailed material listings
- **Add to Cart** — Add materials to cart with quantity selection
- **Buy Now** — Instant purchase option
- **Checkout & Payment** — Complete order placement with multiple payment methods (Razorpay, UPI, COD, Bank Transfer)

### 📦 Order Management
- Place, track, and cancel orders
- Real-time order status tracking (Placed → Processing → Shipped → Delivered)
- Order detail view with itemized breakdown

### 👥 User & Role Management
- User registration with Admin/Staff roles
- Secure login with CAPTCHA verification
- Forgot password with OTP verification via email
- Role-based access control

### 🏢 Supplier Management
- Add, edit, and manage supplier profiles
- Supplier logos and company details
- GST number tracking and specialization

### 🧱 Material & Category Management
- Material categories with parent-child hierarchy
- Detailed material listings with photos, pricing, and stock quantities
- Material search with auto-suggestions
- Quality status tracking (Good / Average / Poor)

### 🏗️ Project Site Management
- Create and manage construction project sites
- GPS coordinates (latitude/longitude) support
- Admin approval workflow (Pending → Approved / Rejected)

### 📊 Inventory & Delivery
- Track available and used quantities per project site
- Delivery management with status tracking and photo proof
- Real-time inventory updates

### 🔔 Notifications & Reviews
- In-app notification system
- Material and supplier review/rating system

---

## 🛠️ Tech Stack

| Layer        | Technology                          |
|-------------|-------------------------------------|
| **Backend**  | Python 3.10+, Django 4.2            |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Database** | MySQL 8.0                           |
| **Server**   | Django Development Server / XAMPP   |

---

## 📁 Project Structure

```
material/
├── generate_ppt.py            # Presentation generator script
├── main.py                    # Entry point
├── .gitignore
├── shop/                      # Django project root
│   ├── manage.py
│   ├── shop/                  # Django settings & config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── customer/              # Main application
│   │   ├── models.py          # 13 database models
│   │   ├── views.py           # All view functions
│   │   ├── admin.py           # Admin panel config
│   │   └── templates/         # HTML templates
│   │       ├── frontpage.html
│   │       ├── dashboard.html
│   │       ├── login.html
│   │       ├── material.html
│   │       ├── material_detail.html
│   │       ├── cart.html
│   │       ├── checkout.html
│   │       └── ... (30+ templates)
│   ├── media/                 # Uploaded files
│   │   ├── documents/         # Supplier logos
│   │   └── materials/         # Material photos
│   └── populate_data.py       # Sample data scripts
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/manvitgm/Buildtrack.git
   cd Buildtrack
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install django mysqlclient pillow
   ```

4. **Configure the database**
   
   Create a MySQL database named `shop`:
   ```sql
   CREATE DATABASE shop;
   ```
   
   Update `shop/shop/settings.py` with your MySQL credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'shop',
           'USER': 'root',
           'PASSWORD': 'your_password',
           'HOST': '127.0.0.1',
           'PORT': '3306',
       }
   }
   ```

5. **Run migrations**
   ```bash
   cd shop
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Populate sample data (optional)**
   ```bash
   python populate_data.py
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Open in browser**
   
   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 💡 Usage

| Action                  | URL                          |
|------------------------|------------------------------|
| Home / Frontpage        | `/`                          |
| Dashboard               | `/dashboard/`                |
| Browse Materials        | `/viewmaterial/`             |
| View Cart               | `/viewcart/`                 |
| Checkout                | `/checkout/`                 |
| Manage Orders           | `/viewmaterialorder/`        |
| Manage Suppliers        | `/viewsupplier/`             |
| Manage Inventory        | `/viewinventory/`            |
| View Notifications      | `/viewnotification/`         |

---

## 🗄️ Models

The system includes **13 interconnected models**:

| #  | Model                | Description                              |
|----|---------------------|------------------------------------------|
| 1  | `userregistration`   | User accounts with role-based access     |
| 2  | `supplier`           | Supplier profiles and company details    |
| 3  | `materialcategory`   | Material categories with hierarchy       |
| 4  | `material`           | Materials with pricing and stock info    |
| 5  | `projectsite`        | Construction project sites               |
| 6  | `cart`               | Shopping cart (Amazon-style)             |
| 7  | `materialorder`      | Purchase orders with status tracking     |
| 8  | `orderitem`          | Individual items within an order         |
| 9  | `payment`            | Payment records with multiple methods    |
| 10 | `delivery`           | Delivery tracking with photo proof       |
| 11 | `inventory`          | Stock levels per project site            |
| 12 | `notification`       | In-app notifications                     |
| 13 | `review`             | Material and supplier reviews/ratings    |

---

## 🔮 Future Enhancements

- 📱 **Mobile Application** — Dedicated Android & iOS app
- 🤖 **AI Integration** — Predictive analytics & demand forecasting
- ☁️ **Cloud Deployment** — AWS/Azure for high availability
- 🔌 **REST API** — Third-party and ERP integration
- 📡 **IoT Integration** — RFID & sensor-based inventory tracking
- 🌐 **Multi-language Support** — Regional language interfaces

---

## 👨‍💻 Author

**Manvit G M**  
📧 Karnataka Science College, Dharwad  
🎓 Department of Computer Science  
🆔 UUCMS: U02AB23S0350

---

## 📄 License

This project is developed as an academic project for educational purposes.
