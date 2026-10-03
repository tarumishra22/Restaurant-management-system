# Restaurant Management System (Backend API)

A RESTful backend service built with **Python**, **Django**, and **Django REST Framework (DRF)** to handle core restaurant operations, including inventory deduction, table reservations, order management, and reporting.

---

## Features

- **Menu Management:** View active dishes with dynamic pricing and availability flags.
- **Table Availability:** Real-time lookup of vacant dining tables.
- **Order Processing & Inventory Auto-Deduct:** Transaction-safe order placement that verifies stock, occupies the table, and automatically deducts recipe ingredients.
- **Table Reservations:** Collision detection logic preventing double-bookings within a 2-hour window while checking seating capacity.
- **Admin Dashboard:** Built-in Django Admin interface to manage tables, inventory, and menu items visually.
- **Reporting & Alerts:** Live endpoints for daily sales revenue and low-stock pantry warnings.

---

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** SQLite (default file-based storage)
- **Language:** Python 3.x

---

## Setup & Local Installation

1. **Clone the repository:**
   ```bash
   git clone <YOUR_REPO_URL>
   cd restaurant-management-system
