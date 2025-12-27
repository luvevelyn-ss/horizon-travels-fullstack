# StudentName=Shune Pyae Pyae Aung
# StudentID=24028257
import os
import re
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request,
    jsonify, session, flash, redirect, url_for
)
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask import make_response
import csv

# Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "shunepyaepyaeaung127304",
    "database": "horizon_travels",
    "auth_plugin": "mysql_native_password"
}

# Admin credentials
admin_email = 'admin@gmail.com'
admin_password = 'admin123'

# Hash the admin password and store as string
hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insert admin if not exists
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM admins WHERE email = %s", (admin_email,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admins (email, password) VALUES (%s, %s)",
            (admin_email, hashed_password)
        )
        conn.commit()
        print("✅ Admin user inserted successfully!")
    cursor.close()
    conn.close()
except Error as e:
    print("❌ Admin setup error:", e)

# Flask app setup
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# Helper functions
def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print("❌ Database connection error:", e)
        return None

def is_valid_email(email: str) -> bool:
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id") or not session.get("is_admin"):
            flash("Administrator access required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    print("📦 Received payment data:", data)

    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Failed to connect to database")

        cursor = conn.cursor()

        # Get current user ID from session
        user_id = session.get("user_id", 1)

        # Parse travel date from input
        travel_date = datetime.strptime(data['travelDate'], "%Y-%m-%d").date()

        # Look up the correct flight_id based on from/to city names
        cursor.execute("""
            SELECT f.id
            FROM flights f
            JOIN cities a ON f.from_city_id = a.id
            JOIN cities b ON f.to_city_id = b.id
            WHERE a.name = %s AND b.name = %s
            LIMIT 1
        """, (data['from'], data['to']))

        flight = cursor.fetchone()
        if not flight:
            raise Exception("No matching flight found for selected route.")

        flight_id = flight[0]

        # Insert booking
        cursor.execute("""
            INSERT INTO bookings (user_id, travel_date, passengers, class, discount_rate, total_amount, flight_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'confirmed')
        """, (
            user_id,
            travel_date,
            len(data['seatNumbers']),
            data['type'],
            data['discount'],
            data['final'],
            flight_id
        ))

        booking_id = cursor.lastrowid

        # Insert selected seats
        for seat in data['seatNumbers']:
            cursor.execute(
                "INSERT INTO booking_seats (booking_id, seat_label) VALUES (%s, %s)",
                (booking_id, seat)
            )

        # Insert payment record (optional: link booking_id if needed)
        cursor.execute("""
            INSERT INTO payments
            (booking_id, name, from_city, to_city, travel_date, class_type, seat_numbers, fare, discount, final_amount, duration_minutes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            booking_id,
            data['name'],
            data['from'],
            data['to'],
            travel_date,
            data['type'],
            ','.join(data['seatNumbers']),
            data['fare'],
            data['discount'],
            data['final'],
            data['durationMin']
        ))

        conn.commit()

        # Return booking ID for redirecting to ticket
        return jsonify({'message': 'Payment and booking saved', 'bookingId': booking_id}), 200

    except Exception as err:
        print("❌ Error in process_payment:", err)
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/ticket/<int:booking_id>")
def show_ticket(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            u.full_name AS passenger_name,
            c_from.name AS from_city,
            c_to.name AS to_city,
            b.travel_date,
            b.class,
            b.discount_rate,
            b.total_amount,
            p.fare,
            p.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN flights f ON b.flight_id = f.id
        JOIN cities c_from ON f.from_city_id = c_from.id
        JOIN cities c_to   ON f.to_city_id = c_to.id
        JOIN payments p ON b.id = p.booking_id
        WHERE b.id = %s
    """, (booking_id,))
    
    ticket = cursor.fetchone()

    cursor.execute("SELECT seat_label FROM booking_seats WHERE booking_id = %s", (booking_id,))
    seats = [r["seat_label"] for r in cursor.fetchall()]
    ticket["seat_numbers"] = ", ".join(seats)

    cursor.close()
    conn.close()

    if not ticket:
        return render_template("ticket.html", ticket=None)

    return render_template("ticket.html", ticket=ticket)


@app.route("/booking")
def booking():
    cnx = get_db_connection()
    if not cnx:
        flash("Database unavailable", "danger")
        return render_template(
            "booking.html",
            cities=[], from_city="", to_city="",
            travel_date="", return_date="",
            seats=1, class_type="economy"
        )

    cur = cnx.cursor()
    cur.execute("SELECT name FROM cities ORDER BY name")
    cities = [r[0] for r in cur.fetchall()]
    cur.close()
    cnx.close()

    return render_template(
        "booking.html",
        cities=cities,
        from_city="",
        to_city="",
        travel_date="",
        return_date="",
        seats=1,
        class_type="economy"
    )

@app.route("/api/cities")
def api_cities():
    cnx = get_db_connection()
    if not cnx:
        return jsonify([]), 500
    cur = cnx.cursor()
    cur.execute("SELECT name FROM cities ORDER BY name")
    cities = [r[0] for r in cur.fetchall()]
    cur.close()
    cnx.close()
    return jsonify(cities)

@app.route("/api/flights")
def api_flights():
    frm, to = request.args.get("from"), request.args.get("to")
    cnx = get_db_connection()
    if not cnx:
        return jsonify({"flights": [], "baseFare": 100}), 500

    cur = cnx.cursor(dictionary=True)
    cur.execute("""
      SELECT f.depart_time, f.arrive_time
      FROM flights f
      JOIN cities a ON f.from_city_id = a.id
      JOIN cities b ON f.to_city_id   = b.id
      WHERE a.name=%s AND b.name=%s
      ORDER BY f.id ASC
    """, (frm, to))

    flights = []
    for row in cur.fetchall():
        dep_str = str(row["depart_time"])[:5]   # "HH:MM"
        arr_str = str(row["arrive_time"])  [:5]
        flights.append({"depart": dep_str, "arrive": arr_str})

    # --- base fare query (still using dict cursor) ---
    cur.execute("""
      SELECT fare
      FROM base_fares bf
      JOIN cities a ON bf.from_city_id = a.id
      JOIN cities b ON bf.to_city_id   = b.id
      WHERE a.name=%s AND b.name=%s
    """, (frm, to))
    bf_row = cur.fetchone()
    base_fare = float(bf_row["fare"]) if bf_row else 100.0

    cur.close()
    cnx.close()
    return jsonify({"flights": flights, "baseFare": base_fare})

@app.route("/api/book", methods=["POST"])
def api_book():
    if "user_id" not in session:
        return jsonify({"status":"error","message":"Not logged in"}), 403

    data = request.get_json()
    td = datetime.strptime(data["departureDate"], "%a %b %d %Y").date()
    rd = None
    if data.get("returnDate"):
        rd = datetime.strptime(data["returnDate"], "%a %b %d %Y").date()

    frm, to = [s.strip() for s in data["route"].split("→")]

    passengers   = data.get("passengers")
    class_type   = data.get("classType")
    total_amount = data.get("totalAmount")

    if not all([td, frm, to, passengers, class_type, total_amount]):
        return jsonify({"status":"error","message":"Missing required data"}), 400

    cnx = get_db_connection()
    cur = cnx.cursor()

    # find outbound flight ID
    cur.execute("""
      SELECT f.id
      FROM flights f
      JOIN cities a ON f.from_city_id = a.id
      JOIN cities b ON f.to_city_id   = b.id
      WHERE a.name=%s AND b.name=%s
      LIMIT 1
    """, (frm, to))
    out = cur.fetchone()
    out_id = out[0] if out else None

    # find return flight ID
    ret_id = None
    if rd:
        cur.execute("""
          SELECT f.id
          FROM flights f
          JOIN cities a ON f.from_city_id = a.id
          JOIN cities b ON f.to_city_id   = b.id
          WHERE a.name=%s AND b.name=%s
          LIMIT 1
        """, (to, frm))
        r = cur.fetchone()
        ret_id = r[0] if r else None

    # calculate discount
    today = datetime.utcnow().date()
    adv   = (td - today).days
    disc  = 0.0
    if adv >= 80:      disc = 0.25
    elif adv >= 60:    disc = 0.15
    elif adv >= 45:    disc = 0.1

    # insert booking (with user_id)
    cur.execute("""
      INSERT INTO bookings
        (user_id, travel_date, return_date, passengers, class,
         discount_rate, total_amount, flight_id, return_flight_id)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
      session["user_id"], td, rd,
      passengers, class_type, disc,
      total_amount, out_id, ret_id
    ))
    booking_id = cur.lastrowid

    # insert seats
    for seat in data["selectedSeats"]:
        cur.execute(
          "INSERT INTO booking_seats (booking_id, seat_label) VALUES (%s,%s)",
          (booking_id, seat)
        )

    cnx.commit()
    cur.close()
    cnx.close()

    return jsonify({"status":"ok","bookingId":booking_id}), 201


@app.route('/manage_booking')
def manage_booking():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        b.id,
        c1.name AS from_city,
        c2.name AS to_city,
        b.travel_date,
        b.return_date,
        b.passengers AS seats,
        b.class AS class_type,
        b.total_amount,
        b.status,
        f.depart_time,
        f.arrive_time
    FROM bookings b
    JOIN flights f ON b.flight_id = f.id
    JOIN cities c1 ON f.from_city_id = c1.id
    JOIN cities c2 ON f.to_city_id = c2.id
    WHERE b.user_id = %s AND b.status = 'confirmed'
    ORDER BY b.travel_date
    """
    cursor.execute(query, (user_id,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('manage_booking.html', bookings=bookings)


@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status = 'cancelled'
        WHERE id = %s AND user_id = %s
    """, (booking_id, session['user_id']))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('manage_booking'))




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Check admin login
        cur.execute("SELECT * FROM admins WHERE email = %s", (email,))
        admin = cur.fetchone()
        if admin:
            if bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
                session['user_id'] = admin['id']
                session['email'] = admin['email']
                session['is_admin'] = True
                cur.close()
                conn.close()
                return redirect(url_for("admin_dashboard"))
            else:
                cur.close()
                conn.close()
                return render_template("login.html", error="Incorrect password for admin account.")

        # Check regular user login
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            if check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['is_admin'] = False
                cur.close()
                conn.close()
                return redirect(url_for("booking"))
            else:
                cur.close()
                conn.close()
                return render_template("login.html", error="Incorrect password. Try again.")
        else:
            cur.close()
            conn.close()
            return render_template("login.html", error="No account found. Please sign up.")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form
        full_name = data.get("fullName", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        if not all([full_name, email, password]):
            return render_template("signup.html", error="All fields are required")
        if len(full_name) < 3:
            return render_template("signup.html", error="Name must be at least 3 characters")
        if not is_valid_email(email):
            return render_template("signup.html", error="Invalid email format")
        if len(password) < 8:
            return render_template("signup.html", error="Password must be at least 8 characters")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return render_template("signup.html", error="Email already registered")

        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                    (full_name, email, hashed))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Summary counts
        cur.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cur.fetchone()["total_users"]

        cur.execute("SELECT COUNT(*) AS total_flights FROM flights")
        total_flights = cur.fetchone()["total_flights"]

        cur.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
        total_bookings = cur.fetchone()["total_bookings"]

        cur.execute("SELECT SUM(total_amount) AS total_revenue FROM bookings WHERE status = 'confirmed'")
        total_revenue = cur.fetchone()["total_revenue"] or 0.0

        # Recent bookings
        cur.execute("""
            SELECT u.full_name, c1.name AS from_city, c2.name AS to_city, b.travel_date, b.status
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN flights f ON b.flight_id = f.id
            JOIN cities c1 ON f.from_city_id = c1.id
            JOIN cities c2 ON f.to_city_id = c2.id
            ORDER BY b.id DESC
            LIMIT 3
        """)
        recent = cur.fetchall()

        # Cancelled count
        cur.execute("SELECT COUNT(*) AS cancelled FROM bookings WHERE status = 'cancelled'")
        cancelled = cur.fetchone()["cancelled"]

        # Class distribution for pie chart
        class_labels = ['Economy', 'Business']
        class_counts = [0, 0]
        cur.execute("SELECT class, COUNT(*) as count FROM bookings GROUP BY class")
        for row in cur.fetchall():
            if row['class'] == 'economy':
                class_counts[0] = row['count']
            elif row['class'] == 'business':
                class_counts[1] = row['count']

        # Monthly earnings (sample data, replace with real monthly aggregation later)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        earnings = [1200, 1500, 1100, 1800, 2000, 1700]  # TODO: calculate dynamically if needed

        cur.close()
        conn.close()

        return render_template(
            "admin_dashboard.html",
            section='overview',
            total_users=total_users,
            total_flights=total_flights,
            total_bookings=total_bookings,
            total_revenue=total_revenue,
            recent=recent,
            cancelled=cancelled,
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            months=months,
            earnings=earnings,
            class_labels=class_labels,
            class_counts=class_counts
        )

    except Exception as e:
        print("\u274c Error in admin_dashboard:", e)
        return f"<h2>Admin Dashboard Error</h2><p>{str(e)}</p>", 500



@app.route("/admin/users")
def manage_users():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, full_name, email FROM users ORDER BY id DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Users</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 30px; }
            h2 { color: #333; margin-bottom: 20px; }
            .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: left; }
            th { background-color: #f8f9fa; color: #333; }
            .btn { padding: 8px 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; }
            .edit-btn { background-color: #ffc107; color: black; }
            .delete-btn { background-color: #dc3545; color: white; }
            .edit-btn:hover { background-color: #e0a800; }
            .delete-btn:hover { background-color: #c82333; }
            a.back { display: inline-block; margin-bottom: 15px; color: #007BFF; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class='card'>
            <h2>Manage Users</h2>
            <a href='/admin_dashboard' class='back'>&larr; Back to Dashboard</a>
            <table>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Actions</th></tr>
    """

    for u in users:
        html += f"""
                <tr>
                    <td>{u['id']}</td>
                    <td>{u['full_name']}</td>
                    <td>{u['email']}</td>
                    <td>
                        <form method='GET' action='/admin/users/edit/{u['id']}' style='display:inline;'>
                            <button class='btn edit-btn'>Edit</button>
                        </form>
                        <form method='POST' action='/admin/users/delete/{u['id']}' style='display:inline;' onsubmit='return confirm("Delete this user?");'>
                            <button class='btn delete-btn'>Delete</button>
                        </form>
                    </td>
                </tr>
        """

    html += """
            </table>
        </div>
    </body>
    </html>
    """
    return html





@app.route("/admin/journeys")
def manage_journeys():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT f.id, a.name AS from_city, b.name AS to_city, 
               f.depart_time, f.arrive_time
        FROM flights f
        JOIN cities a ON f.from_city_id = a.id
        JOIN cities b ON f.to_city_id = b.id
        ORDER BY f.id DESC
    """)
    journeys = cur.fetchall()
    cur.close()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Journeys</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f0f2f5;
                padding: 30px;
            }
            h2 {
                color: #333;
                margin-bottom: 20px;
            }
            .card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            table.responsive-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px 15px;
                text-align: left;
            }
            th {
                background-color: #f8f9fa;
                color: #333;
            }
            .btn {
                padding: 8px 14px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                font-weight: bold;
            }
            .edit-btn {
                background-color: #ffc107;
                color: black;
            }
            .delete-btn {
                background-color: #dc3545;
                color: white;
            }
            .edit-btn:hover {
                background-color: #e0a800;
            }
            .delete-btn:hover {
                background-color: #c82333;
            }
            a.back {
                display: inline-block;
                margin-bottom: 15px;
                color: #007BFF;
                text-decoration: none;
            }

            @media (max-width: 768px) {
                table.responsive-table thead {
                    display: none;
                }
                table.responsive-table tr {
                    display: block;
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    background: white;
                    padding: 10px;
                }
                table.responsive-table td {
                    display: block;
                    text-align: left;
                    padding-left: 50%;
                    position: relative;
                    border: none;
                    border-bottom: 1px solid #eee;
                }
                table.responsive-table td::before {
                    content: attr(data-label);
                    position: absolute;
                    left: 15px;
                    top: 12px;
                    font-weight: bold;
                    white-space: nowrap;
                }
            }
        </style>
    </head>
    <body>
        <div class='card'>
            <h2>Manage Journeys</h2>
            <a href='/admin_dashboard' class='back'>&larr; Back to Dashboard</a>
            <table class='responsive-table'>
                <thead>
                    <tr><th>ID</th><th>From</th><th>To</th><th>Depart</th><th>Arrive</th><th>Actions</th></tr>
                </thead>
                <tbody>
    """

    for j in journeys:
        html += f"""
            <tr>
                <td data-label="ID">{j['id']}</td>
                <td data-label="From">{j['from_city']}</td>
                <td data-label="To">{j['to_city']}</td>
                <td data-label="Depart">{j['depart_time']}</td>
                <td data-label="Arrive">{j['arrive_time']}</td>
                <td data-label="Actions">
                    <form method='GET' action='/admin/journeys/edit/{j['id']}' style='display:inline;'>
                        <button class='btn edit-btn'>Edit</button>
                    </form>
                    <form method='POST' action='/admin/journeys/delete/{j['id']}' style='display:inline;' onsubmit='return confirm("Delete this journey?");'>
                        <button class='btn delete-btn'>Delete</button>
                    </form>
                </td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/admin/bookings")
def manage_bookings():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    keyword = request.args.get("q", "").lower()
    selected_class = request.args.get("class", "").lower()
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT b.id, u.full_name, a.name AS from_city, b2.name AS to_city,
               b.travel_date, b.return_date, b.passengers, b.class,
               b.total_amount, b.created_at
        FROM bookings b
        JOIN users u       ON b.user_id = u.id
        JOIN flights f     ON b.flight_id = f.id
        JOIN cities a      ON f.from_city_id = a.id
        JOIN cities b2     ON f.to_city_id = b2.id
        ORDER BY b.id DESC
    """)
    all_bookings = cur.fetchall()
    cur.close()
    conn.close()

    def matches_date(b):
        if start_date and b['travel_date'] < start_date:
            return False
        if end_date and b['travel_date'] > end_date:
            return False
        return True

    bookings = [b for b in all_bookings
                if (keyword in b['full_name'].lower() or keyword in b['from_city'].lower() or keyword in b['to_city'].lower())
                and (b['class'].lower() == selected_class if selected_class else True)
                and matches_date(b)]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Bookings</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 30px; }}
            h2 {{ color: #333; margin-bottom: 20px; }}
            .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
            table.responsive-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px 15px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #333; }}
            form.search-form {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 15px; }}
            input[type='text'], input[type='date'], select {{ padding: 8px; border-radius: 6px; border: 1px solid #ccc; }}
            .btn {{ padding: 8px 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; }}
            .btn-search {{ background-color: #28a745; color: white; }}
            .btn-search:hover {{ background-color: #218838; }}
            .edit-btn {{ background-color: #ffc107; color: black; }}
            .cancel-btn {{ background-color: #dc3545; color: white; }}
            .clear-btn {{ background-color: #6c757d; color: white; }}
            .edit-btn:hover {{ background-color: #e0a800; }}
            .cancel-btn:hover {{ background-color: #c82333; }}
            .clear-btn:hover {{ background-color: #5a6268; }}
            a.back {{ display: inline-block; margin-bottom: 15px; color: #007BFF; text-decoration: none; }}

            @media (max-width: 768px) {{
                table.responsive-table thead {{ display: none; }}
                table.responsive-table tr {{
                    display: block;
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    background: white;
                    padding: 10px;
                }}
                table.responsive-table td {{
                    display: block;
                    text-align: left;
                    padding-left: 50%;
                    position: relative;
                    border: none;
                    border-bottom: 1px solid #eee;
                }}
                table.responsive-table td::before {{
                    content: attr(data-label);
                    position: absolute;
                    left: 15px;
                    top: 12px;
                    font-weight: bold;
                    white-space: nowrap;
                }}
            }}
        </style>
    </head>
    <body>
        <div class='card'>
            <h2>Manage Bookings</h2>
            <a href='/admin_dashboard' class='back'>&larr; Back to Dashboard</a>
            <form class='search-form' method='get'>
                <input type='text' name='q' placeholder='Search by name or city' value='{keyword}'>
                <select name='class'>
                    <option value=''>All Classes</option>
                    <option value='economy' {'selected' if selected_class == 'economy' else ''}>Economy</option>
                    <option value='business' {'selected' if selected_class == 'business' else ''}>Business</option>
                </select>
                <input type='date' name='start_date' value='{start_date}'>
                <input type='date' name='end_date' value='{end_date}'>
                <button type='submit' class='btn btn-search'>Search</button>
                <a href='/admin/bookings' class='btn clear-btn'>Clear</a>
            </form>
            <table class='responsive-table'>
                <thead>
                    <tr>
                        <th>ID</th><th>User</th><th>From</th><th>To</th>
                        <th>Travel Date</th><th>Return Date</th><th>Passengers</th>
                        <th>Class</th><th>Total (£)</th><th>Booked At</th><th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    """

    for b in bookings:
        return_date = b['return_date'] if b['return_date'] else "-"
        booked_at = b['created_at'].strftime('%Y-%m-%d') if b['created_at'] else "-"
        html += f"""
            <tr>
                <td data-label="ID">{b['id']}</td>
                <td data-label="User">{b['full_name']}</td>
                <td data-label="From">{b['from_city']}</td>
                <td data-label="To">{b['to_city']}</td>
                <td data-label="Travel Date">{b['travel_date']}</td>
                <td data-label="Return Date">{return_date}</td>
                <td data-label="Passengers">{b['passengers']}</td>
                <td data-label="Class">{b['class']}</td>
                <td data-label="Total (£)">£{b['total_amount']}</td>
                <td data-label="Booked At">{booked_at}</td>
                <td data-label="Actions">
                    <form style='display:inline;' method='GET' action='/admin/bookings/edit/{b['id']}'>
                        <button class='btn edit-btn' type='submit'>Edit</button>
                    </form>
                    <form style='display:inline;' method='POST' action='/admin/bookings/delete/{b['id']}' onsubmit='return confirm("Cancel this booking?");'>
                        <button class='btn cancel-btn' type='submit'>Cancel</button>
                    </form>
                </td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html


# ✅ Updated `/admin/fares` route with responsive layout

@app.route("/admin/fares", methods=["GET", "POST"])
def update_fares():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    keyword = request.args.get("q", "").lower()

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT bf.id, a.name AS from_city, b.name AS to_city, bf.fare
        FROM base_fares bf
        JOIN cities a ON bf.from_city_id = a.id
        JOIN cities b ON bf.to_city_id = b.id
        ORDER BY a.name, b.name
    """)
    fares = cur.fetchall()

    if request.method == "POST":
        fare_id = request.form.get("fare_id")
        new_fare = request.form.get("fare")
        cur.execute("UPDATE base_fares SET fare = %s WHERE id = %s", (new_fare, fare_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("update_fares"))

    cur.close()
    conn.close()

    filtered_fares = [f for f in fares if keyword in f['from_city'].lower() or keyword in f['to_city'].lower()] if keyword else fares

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Update Fares</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 30px; }}
            h2 {{ color: #333; margin-bottom: 20px; }}
            .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
            table.responsive-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px 15px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #333; }}
            .btn {{ padding: 8px 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; }}
            .btn-save {{ background-color: #28a745; color: white; }}
            .btn-save:hover {{ background-color: #218838; }}
            .btn-clear {{ background-color: #6c757d; color: white; }}
            .btn-clear:hover {{ background-color: #5a6268; }}
            input[type='number'] {{ width: 80px; padding: 6px; border-radius: 4px; border: 1px solid #ccc; }}
            form.inline {{ display: flex; gap: 10px; align-items: center; }}
            a.back {{ display: inline-block; margin-bottom: 15px; color: #007BFF; text-decoration: none; }}
            form.search-form {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 15px; }}
            input[type='text'] {{ padding: 6px; border-radius: 4px; border: 1px solid #ccc; width: 220px; }}
            .btn-search {{ background-color: #28a745; color: white; }}
            .btn-search:hover {{ background-color: #218838; }}

            @media (max-width: 768px) {{
                table.responsive-table thead {{ display: none; }}
                table.responsive-table tr {{
                    display: block;
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    background: white;
                    padding: 10px;
                }}
                table.responsive-table td {{
                    display: block;
                    text-align: left;
                    padding-left: 50%;
                    position: relative;
                    border: none;
                    border-bottom: 1px solid #eee;
                }}
                table.responsive-table td::before {{
                    content: attr(data-label);
                    position: absolute;
                    left: 15px;
                    top: 12px;
                    font-weight: bold;
                    white-space: nowrap;
                }}
            }}
        </style>
    </head>
    <body>
        <div class='card'>
            <h2>Update Base Fares</h2>
            <a href='/admin_dashboard' class='back'>&larr; Back to Dashboard</a>
            <form method='get' class='search-form'>
                <input type='text' name='q' placeholder='Search from/to city' value='{keyword}'>
                <button type='submit' class='btn btn-search'>Search</button>
                <a href='/admin/fares' class='btn btn-clear'>Clear</a>
            </form>
            <table class='responsive-table'>
                <thead>
                    <tr><th>From</th><th>To</th><th>Fare (£)</th><th>Update</th></tr>
                </thead>
                <tbody>
    """

    for f in filtered_fares:
        html += f"""
            <tr>
                <td data-label="From">{f['from_city']}</td>
                <td data-label="To">{f['to_city']}</td>
                <td data-label="Fare (£)">£{f['fare']:.2f}</td>
                <td data-label="Update">
                    <form class='inline' method='POST'>
                        <input type='hidden' name='fare_id' value='{f['id']}'>
                        <input type='number' step='0.01' name='fare' value='{f['fare']}' required>
                        <button class='btn btn-save' type='submit'>Save</button>
                    </form>
                </td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/admin/reports")
def admin_reports():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cur.fetchone()['total_users']

    cur.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
    total_bookings = cur.fetchone()['total_bookings']

    cur.execute("SELECT SUM(total_amount) AS total_revenue FROM bookings")
    total_revenue = cur.fetchone()['total_revenue'] or 0.0

    cur.execute("""
        SELECT class, COUNT(*) AS count
        FROM bookings
        GROUP BY class
    """)
    class_counts = cur.fetchall()

    cur.execute("""
        SELECT DATE(created_at) AS date, COUNT(*) AS count
        FROM bookings
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 10
    """)
    recent_activity = cur.fetchall()

    cur.close()
    conn.close()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Reports</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 30px; }}
            h2 {{ color: #333; margin-bottom: 20px; }}
            .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }}
            .metric {{ font-size: 1.2em; margin: 8px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px 12px; text-align: left; }}
            th {{ background-color: #f8f9fa; }}
            a.back {{ display: inline-block; margin-bottom: 15px; color: #007BFF; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class='card'>
            <h2>Admin Reports</h2>
            <a href='/admin_dashboard' class='back'>&larr; Back to Dashboard</a>
            <div class='metric'>📊 Total Users: <strong>{total_users}</strong></div>
            <div class='metric'>✈️ Total Bookings: <strong>{total_bookings}</strong></div>
            <div class='metric'>💰 Total Revenue: <strong>£{total_revenue:.2f}</strong></div>
        </div>

        <div class='card'>
            <h3>Bookings by Class</h3>
            <table>
                <tr><th>Class</th><th>Number of Bookings</th></tr>
    """
    for row in class_counts:
        html += f"<tr><td>{row['class'].capitalize()}</td><td>{row['count']}</td></tr>"

    html += """
            </table>
        </div>

        <div class='card'>
            <h3>Recent Booking Activity</h3>
            <table>
                <tr><th>Date</th><th>Bookings</th></tr>
    """
    for r in recent_activity:
        html += f"<tr><td>{r['date']}</td><td>{r['count']}</td></tr>"

    html += """
            </table>
        </div>
    </body>
    </html>
    """
    return html



@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    try:
        conn = get_db_connection()
        conn.close()
    except Error as e:
        print("❌ Startup DB error:", e)
        exit(1)

    app.run(debug=True)