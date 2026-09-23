from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = "database.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLES ----------------

def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('collector', 'recycler'))
        )
    """)

    # Scrap listings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collector_id INTEGER NOT NULL,
            scrap_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            location TEXT NOT NULL,
            price REAL DEFAULT 0,
            status TEXT DEFAULT 'available',
            FOREIGN KEY (collector_id) REFERENCES users(id)
        )
    """)

    # Requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scrap_id INTEGER NOT NULL,
            recycler_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (scrap_id) REFERENCES scrap(id),
            FOREIGN KEY (recycler_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to ScrapSetu Backend",
        "status": "Backend is running"
    })


# =====================================================
# USER AUTHENTICATION
# =====================================================

# ---------------- REGISTER ----------------

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    if role not in ["collector", "recycler"]:
        return jsonify({
            "success": False,
            "message": "Role must be collector or recycler"
        }), 400

    hashed_password = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password, role))

        conn.commit()

        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user_id": user_id
        }), 201

    except sqlite3.IntegrityError:

        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 409

    finally:
        conn.close()


# ---------------- LOGIN ----------------

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user["password"], password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    })


# =====================================================
# USER PROFILE
# =====================================================

@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, role
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "user": dict(user)
    })


# =====================================================
# SCRAP LISTINGS
# =====================================================

# ---------------- ADD SCRAP ----------------

@app.route("/api/scrap", methods=["POST"])
def add_scrap():

    data = request.get_json()

    collector_id = data.get("collector_id")
    scrap_type = data.get("scrap_type")
    quantity = data.get("quantity")
    location = data.get("location")
    price = data.get("price", 0)

    if not collector_id or not scrap_type or not quantity or not location:
        return jsonify({
            "success": False,
            "message": "Collector ID, scrap type, quantity and location are required"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    # Check collector
    cursor.execute("""
        SELECT * FROM users
        WHERE id = ? AND role = 'collector'
    """, (collector_id,))

    collector = cursor.fetchone()

    if collector is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Invalid collector"
        }), 400

    cursor.execute("""
        INSERT INTO scrap
        (collector_id, scrap_type, quantity, location, price)
        VALUES (?, ?, ?, ?, ?)
    """, (
        collector_id,
        scrap_type,
        quantity,
        location,
        price
    ))

    conn.commit()

    scrap_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "message": "Scrap listing created",
        "scrap_id": scrap_id
    }), 201


# ---------------- GET ALL SCRAP ----------------

@app.route("/api/scrap", methods=["GET"])
def get_scrap():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            scrap.id,
            scrap.scrap_type,
            scrap.quantity,
            scrap.location,
            scrap.price,
            scrap.status,
            users.name AS collector_name
        FROM scrap
        JOIN users
        ON scrap.collector_id = users.id
        ORDER BY scrap.id DESC
    """)

    scraps = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "scrap": [dict(item) for item in scraps]
    })


# ---------------- GET COLLECTOR'S SCRAP ----------------

@app.route("/api/scrap/collector/<int:collector_id>", methods=["GET"])
def get_collector_scrap(collector_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM scrap
        WHERE collector_id = ?
        ORDER BY id DESC
    """, (collector_id,))

    scraps = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "scrap": [dict(item) for item in scraps]
    })


# ---------------- UPDATE SCRAP ----------------

@app.route("/api/scrap/<int:scrap_id>", methods=["PUT"])
def update_scrap(scrap_id):

    data = request.get_json()

    scrap_type = data.get("scrap_type")
    quantity = data.get("quantity")
    location = data.get("location")
    price = data.get("price")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE scrap
        SET scrap_type = ?,
            quantity = ?,
            location = ?,
            price = ?
        WHERE id = ?
    """, (
        scrap_type,
        quantity,
        location,
        price,
        scrap_id
    ))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Scrap listing not found"
        }), 404

    conn.close()

    return jsonify({
        "success": True,
        "message": "Scrap listing updated"
    })


# ---------------- DELETE SCRAP ----------------

@app.route("/api/scrap/<int:scrap_id>", methods=["DELETE"])
def delete_scrap(scrap_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM scrap
        WHERE id = ?
    """, (scrap_id,))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Scrap listing not found"
        }), 404

    conn.close()

    return jsonify({
        "success": True,
        "message": "Scrap listing deleted"
    })


# =====================================================
# RECYCLER REQUESTS
# =====================================================

# ---------------- CREATE REQUEST ----------------

@app.route("/api/request", methods=["POST"])
def create_request():

    data = request.get_json()

    scrap_id = data.get("scrap_id")
    recycler_id = data.get("recycler_id")

    if not scrap_id or not recycler_id:
        return jsonify({
            "success": False,
            "message": "Scrap ID and Recycler ID are required"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    # Check recycler
    cursor.execute("""
        SELECT * FROM users
        WHERE id = ? AND role = 'recycler'
    """, (recycler_id,))

    recycler = cursor.fetchone()

    if recycler is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Invalid recycler"
        }), 400

    # Check scrap
    cursor.execute("""
        SELECT * FROM scrap
        WHERE id = ?
    """, (scrap_id,))

    scrap = cursor.fetchone()

    if scrap is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Scrap listing not found"
        }), 404

    if scrap["status"] != "available":
        conn.close()

        return jsonify({
            "success": False,
            "message": "Scrap is no longer available"
        }), 400

    cursor.execute("""
        INSERT INTO requests
        (scrap_id, recycler_id)
        VALUES (?, ?)
    """, (scrap_id, recycler_id))

    conn.commit()

    request_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "message": "Request sent successfully",
        "request_id": request_id
    }), 201


# ---------------- GET REQUESTS ----------------

@app.route("/api/requests/recycler/<int:recycler_id>", methods=["GET"])
def get_recycler_requests(recycler_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            requests.id,
            requests.status,
            scrap.scrap_type,
            scrap.quantity,
            scrap.location,
            scrap.price,
            users.name AS collector_name
        FROM requests

        JOIN scrap
        ON requests.scrap_id = scrap.id

        JOIN users
        ON scrap.collector_id = users.id

        WHERE requests.recycler_id = ?

        ORDER BY requests.id DESC
    """, (recycler_id,))

    requests = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "requests": [dict(item) for item in requests]
    })


# ---------------- UPDATE REQUEST STATUS ----------------

@app.route("/api/request/<int:request_id>", methods=["PUT"])
def update_request(request_id):

    data = request.get_json()

    status = data.get("status")

    allowed_status = [
        "pending",
        "accepted",
        "rejected",
        "completed"
    ]

    if status not in allowed_status:
        return jsonify({
            "success": False,
            "message": "Invalid status"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE requests
        SET status = ?
        WHERE id = ?
    """, (status, request_id))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Request not found"
        }), 404

    # If request is accepted, mark scrap as unavailable
    if status == "accepted":

        cursor.execute("""
            SELECT scrap_id
            FROM requests
            WHERE id = ?
        """, (request_id,))

        request_data = cursor.fetchone()

        if request_data:
            cursor.execute("""
                UPDATE scrap
                SET status = 'booked'
                WHERE id = ?
            """, (request_data["scrap_id"],))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Request status updated"
    })


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    create_tables()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )