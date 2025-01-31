from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YSIJTM1MWIEM16a",
            database="fahrradmiete"
        )
        return conn
    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankverbindungsfehler: {err}"}), 500

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    personal_number = data.get("personal_number")
    password = data.get("password")

    if not personal_number:
        return jsonify({"error": "Personalnummer ist erforderlich."}), 400
    if not password:
        return jsonify({"error": "Passwort ist erforderlich."}), 400

    conn = db_connection()
    if isinstance(conn, tuple):
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM user WHERE personal_number = %s", (personal_number,))
        if cursor.fetchone():
            return jsonify({"error": "Diese Personalnummer ist bereits registriert."}), 400

        cursor.execute("INSERT INTO user (personal_number, password, role) VALUES (%s, %s, %s)",
                       (personal_number, password, "user"))
        conn.commit()
        return jsonify({
            "message": "Registrierung erfolgreich.",
            "redirect": "buchung.html"  # Key change: Redirect to booking page
        }), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Registrierung: {err}"}), 500
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    personal_number = data.get("personal_number")
    password = data.get("password")

    if not personal_number:
        return jsonify({"error": "Personalnummer ist erforderlich."}), 400
    if not password:
        return jsonify({"error": "Passwort ist erforderlich."}), 400

    conn = db_connection()
    if isinstance(conn, tuple):
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM user WHERE personal_number = %s AND password = %s",
                       (personal_number, password))
        user = cursor.fetchone()

        if user:
            return jsonify({
                "message": "Anmeldung erfolgreich.",
                "redirect": "auswahl.html",
                "userId": user["id"]
            }), 200
        else:
            return jsonify({"error": "Anmeldung fehlgeschlagen."}), 401

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Anmeldung: {err}"}), 500
    finally:
        conn.close()

@app.route("/booking", methods=["GET", "POST"])
def booking():
    conn = db_connection()
    if isinstance(conn, tuple):
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == "GET":
            # Fetch ALL vehicles (not just available ones)
            cursor.execute("SELECT * FROM item")
            items = cursor.fetchall()
            return jsonify(items), 200

        elif request.method == "POST":
            data = request.json
            user_id = data.get("user_id")
            item_id = data.get("item_id")
            start_date = data.get("start_date")

            if not user_id:
                return jsonify({"error": "Benutzer-ID ist erforderlich."}), 400
            if not item_id:
                return jsonify({"error": "Fahrzeug-ID ist erforderlich."}), 400

            # Check if vehicle is available and battery >=80%
            cursor.execute("SELECT * FROM item WHERE id = %s AND status = 'verfügbar' AND battery_level >= 80", (item_id,))
            item = cursor.fetchone()

            if not item:
                return jsonify({"error": "Fahrzeug nicht verfügbar oder Akku unter 80%."}), 400

            cursor.execute("INSERT INTO booking (user_id, item_id, start_date) VALUES (%s, %s, %s)",
                           (user_id, item_id, start_date))
            booking_id = cursor.lastrowid

            cursor.execute("UPDATE item SET status = 'vermietet' WHERE id = %s", (item_id,))
            conn.commit()
            return jsonify({"message": "Buchung erfolgreich.", "booking_id": booking_id}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler: {err}"}), 500
    finally:
        conn.close()

@app.route("/return", methods=["POST"])
def return_item():
    data = request.json
    booking_id = data.get("booking_id")
    location = data.get("location")

    if not booking_id:
        return jsonify({"error": "Buchungs-ID ist erforderlich."}), 400
    if not location:
        return jsonify({"error": "Standort ist erforderlich."}), 400

    conn = db_connection()
    if isinstance(conn, tuple):
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM booking WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({"error": "Buchung nicht gefunden."}), 400

        cursor.execute("UPDATE booking SET end_date = %s WHERE id = %s",
                       (datetime.now().strftime("%Y-%m-%d"), booking_id))
        cursor.execute("UPDATE item SET status = 'verfügbar', location = %s WHERE id = %s",
                       (location, booking["item_id"]))
        conn.commit()
        return jsonify({"message": "Rückgabe erfolgreich.", "redirect": "auswahl.html"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler: {err}"}), 500
    finally:
        conn.close()

@app.route("/overview", methods=["GET"])
def overview():
    conn = db_connection()
    if isinstance(conn, tuple):
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT u.personal_number, b.start_date, b.end_date, i.id AS item_id, i.type
            FROM booking b
            JOIN user u ON b.user_id = u.id
            JOIN item i ON b.item_id = i.id
        """)
        bookings = cursor.fetchall()
        return jsonify(bookings), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler: {err}"}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)