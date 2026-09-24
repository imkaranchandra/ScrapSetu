# ScrapSetu Backend API ♻️

A modern, high-performance REST API built with **Python**, **FastAPI**, and **SQLite** to power the **ScrapSetu** platform—bridging the gap between Scrap Collectors and Recyclers.

---

## 🌟 Highlights

- **⚡ FastAPI Architecture**: High-speed asynchronous REST API with automatic data validation via Pydantic v2.
- **📄 Interactive API Documentation**: Built-in Swagger UI at `/docs` and ReDoc at `/redoc`.
- **🔐 JWT Authentication & Password Hashing**: Role-based authentication (`collector`, `recycler`, `admin`) using bcrypt.
- **💰 Live Scrap Rates Management**: Seeded default rates for materials (Plastic, Paper, Iron, Copper, Aluminium, Steel, E-Waste).
- **📦 End-to-End Scrap Workflow**:
  1. **Collector** submits scrap with material, weight, pickup address, and estimated valuation.
  2. **Recycler** views incoming lots in real-time.
  3. **Recycler** accepts or rejects lots; upon acceptance, a pickup schedule with driver details is automatically created.
  4. **Logistics & Handover**: Recycler tracks pickup steps and confirms handover upon receiving scrap.
- **🚚 Logistics & Pickup Tracking**: Real-time status tracking (`Lot Accepted` → `Pickup Scheduled` → `Handover Pending` → `Completed`).
- **📊 Analytics & Dashboard**: Instant aggregation of recycled kilograms, total scrap value, and material breakdowns.
- **📁 Scrap Photo Uploads**: Multi-part image upload saved directly to local storage (`/uploads`).
- **🌐 Zero CORS friction**: Configured to work smoothly with any frontend client (`file://`, localhost, or deployed apps).

---

## 📁 Project Structure

```text
Backend/
├── app/
│   ├── __init__.py          # Package initializer
│   ├── main.py              # FastAPI app instance, CORS middleware, lifespan
│   ├── config.py            # Settings (JWT secret, DB URL, upload path)
│   ├── database.py          # SQLAlchemy SQLite connection & session dependency
│   ├── models.py            # Database models (User, ScrapRate, ScrapLot, Pickup)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # Password hashing & JWT token utilities
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Register, Login, Me, Profile endpoints
│       ├── rates.py         # Scrap material rates & price board endpoints
│       ├── scrap.py         # Scrap submission, incoming lots, accept/reject, handover
│       ├── pickups.py       # Active pickups and tracking logistics
│       └── dashboard.py     # Aggregated stats & analytics
├── uploads/                 # Local directory for scrap photos
├── tests/
├── test_endpoints.py        # Complete automated test suite
├── run.py                   # One-click server runner
├── requirements.txt         # Python package dependencies
├── .env.example             # Template for environment variables
└── README.md                # Documentation (this file)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.12 recommended)

### 2. Setup Virtual Environment

Open a terminal in the `Backend` directory:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Backend Server

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will start at:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **Alternative ReDoc UI**: `http://127.0.0.1:8000/redoc`

### 🔑 Default Configured Accounts

| Role | Mobile Number | Password |
|---|---|---|
| **Collector** | `9336864092` | `karancollector` |
| **Recycler** | `9936541942` | `ramrecyclers` |

---

## 🧪 Automated Testing

A complete automated test suite is provided to verify all routes and database transitions:

```bash
python test_endpoints.py
```

---

## 📡 API Endpoint Reference

### 1. Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register a new user (`collector` or `recycler`) | No |
| `POST` | `/api/auth/login` | Login with mobile number and password | No |
| `GET` | `/api/auth/me` | Fetch authenticated user's profile | Bearer Token |
| `PUT` | `/api/auth/profile` | Update profile (name, business name, address) | Bearer Token |

#### Register Request Example:
```json
POST /api/auth/register
{
  "mobile": "9876543210",
  "password": "password123",
  "full_name": "Rohan Kumar",
  "role": "collector",
  "address": "12 Gandhi Path",
  "city": "Mumbai"
}
```

---

### 2. Scrap Rates (`/api/rates`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/rates` | List all scrap rates with units and currency | No |
| `GET` | `/api/rates/dict` | Key-value dictionary `{"Plastic": 20, ...}` | No |
| `PUT` | `/api/rates/{material}` | Update per-kg rate for a material | Optional |
| `POST` | `/api/rates` | Add or update a material rate | Optional |

#### Seeded Rates:
- **Plastic**: ₹20 / kg
- **Paper**: ₹15 / kg
- **Iron**: ₹35 / kg
- **Copper**: ₹600 / kg
- **Aluminium**: ₹120 / kg
- **Steel**: ₹45 / kg
- **E-Waste**: ₹80 / kg

---

### 3. Scrap Lots & Transactions (`/api/scrap`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/scrap` | Collector submits new scrap lot | Optional (auto-assigns default demo collector if omitted) |
| `GET` | `/api/scrap/my-collections` | Collector's submitted lots and statuses | Optional |
| `GET` | `/api/scrap/incoming` | Recycler's view of all pending scrap lots | No |
| `GET` | `/api/scrap/history` | Recycler's accepted and completed transactions | Optional |
| `GET` | `/api/scrap/{lot_id}` | Detailed lot view with collector/recycler/pickup info | No |
| `POST` | `/api/scrap/{lot_id}/accept` | Recycler accepts incoming lot (schedules pickup) | Optional |
| `POST` | `/api/scrap/{lot_id}/reject` | Recycler rejects incoming lot | Optional |
| `POST` | `/api/scrap/{lot_id}/handover` | Recycler confirms physical handover & completes lot | Optional |
| `POST` | `/api/scrap/upload-photo` | Upload scrap image (returns URL) | No |

#### Submit Scrap Request Example:
```json
POST /api/scrap
{
  "material": "Copper",
  "weight": 5.5,
  "pickup_address": "Sector 4, Plot 19, Vashi",
  "collector_notes": "Clean copper pipes and cables"
}
```

---

### 4. Pickups & Logistics (`/api/pickups`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/pickups/active` | Get current active pickup for recycler | Optional |
| `GET` | `/api/pickups/{lot_id}` | Get pickup logistics details for a lot | No |
| `PATCH` | `/api/pickups/{lot_id}` | Update driver, vehicle number, or tracking step | Optional |

---

### 5. Dashboard & Analytics (`/api/dashboard`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/stats` | Aggregated metrics: total lots, completed lots, total kg, total value, and breakdown by material |

---

## 🔒 Security Best Practices Implemented

- Passwords stored as **bcrypt** salted hashes (never plaintext).
- **JWT (JSON Web Tokens)** standard with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Database constraints with foreign key cascades and unique constraints on user mobiles and lot numbers.
- SQL injection prevention via **SQLAlchemy ORM** parameterized queries.
