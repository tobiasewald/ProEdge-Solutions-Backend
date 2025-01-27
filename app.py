from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def db_connection():
    """
    Stellt eine Verbindung zur MySQL-Datenbank her.
    :return: Die Datenbankverbindung.
    """
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
    """
    Registriert einen neuen Benutzer.
    :return: JSON-Antwort mit Erfolgsmeldung oder Fehler.
    """
    data = request.json
    personal_number = data.get("personal_number")
    password = data.get("password")

    if not personal_number:
        return jsonify({"error": "Personalnummer ist erforderlich."}), 400
    if not password:
        return jsonify({"error": "Passwort ist erforderlich."}), 400

    conn = db_connection()
    if isinstance(conn, tuple):  # Wenn ein Fehler aufgetreten ist
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        # Überprüfen, ob die Personalnummer bereits existiert
        cursor.execute("SELECT * FROM user WHERE personal_number = %s", (personal_number,))
        if cursor.fetchone():
            return jsonify({"error": "Diese Personalnummer ist bereits registriert."}), 400

        # Neuen Benutzer in die Datenbank einfügen
        cursor.execute("INSERT INTO user (personal_number, password, role) VALUES (%s, %s, %s)",
                       (personal_number, password, "user"))
        conn.commit()
        return jsonify({"message": "Registrierung erfolgreich.", "redirect": "buchung.html"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Registrierung: {err}"}), 500

    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    """
    Meldet einen Benutzer an.
    :return: JSON-Antwort mit Erfolgsmeldung oder Fehler.
    """
    data = request.json
    personal_number = data.get("personal_number")
    password = data.get("password")

    if not personal_number:
        return jsonify({"error": "Personalnummer ist erforderlich."}), 400
    if not password:
        return jsonify({"error": "Passwort ist erforderlich."}), 400

    conn = db_connection()
    if isinstance(conn, tuple):  # Wenn ein Fehler aufgetreten ist
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        # Überprüfen der Anmeldedaten
        cursor.execute("SELECT * FROM user WHERE personal_number = %s AND password = %s",
                       (personal_number, password))
        user = cursor.fetchone()

        if user:
            return jsonify({"message": "Anmeldung erfolgreich.", "redirect": "auswahl.html"}), 200
        else:
            return jsonify({"error": "Anmeldung fehlgeschlagen. Überprüfen Sie Ihre Personalnummer und Ihr Passwort."}), 401

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Anmeldung: {err}"}), 500

    finally:
        conn.close()

@app.route("/booking", methods=["GET", "POST"])
def booking():
    """
    Handhabt die Buchung von Fahrzeugen.
    - GET: Gibt alle verfügbaren Fahrzeuge zurück.
    - POST: Erstellt eine neue Buchung.
    :return: JSON-Antwort mit den verfügbaren Fahrzeugen oder Buchungsbestätigung.
    """
    conn = db_connection()
    if isinstance(conn, tuple):  # Wenn ein Fehler aufgetreten ist
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == "GET":
            # Alle verfügbaren Fahrzeuge mit Akkustand >= 80% abrufen
            cursor.execute("SELECT * FROM item WHERE status = 'verfügbar' AND battery_level >= 80")
            items = cursor.fetchall()
            return jsonify(items), 200

        elif request.method == "POST":
            data = request.json
            user_id = data.get("user_id")
            item_id = data.get("item_id")
            start_date = data.get("start_date")

            # Überprüfen, ob alle erforderlichen Felder angegeben wurden
            if not user_id:
                return jsonify({"error": "Benutzer-ID ist erforderlich."}), 400
            if not item_id:
                return jsonify({"error": "Fahrzeug-ID ist erforderlich."}), 400
            if not start_date:
                return jsonify({"error": "Startdatum ist erforderlich."}), 400

            # Überprüfen, ob das Fahrzeug verfügbar ist und der Akkustand ausreicht
            cursor.execute("SELECT * FROM item WHERE id = %s AND status = 'verfügbar' AND battery_level >= 80", (item_id,))
            item = cursor.fetchone()

            if not item:
                return jsonify({"error": "Das Fahrzeug ist nicht verfügbar oder der Akkustand ist unter 80%."}), 400

            # Neue Buchung erstellen
            cursor.execute("INSERT INTO booking (user_id, item_id, start_date) VALUES (%s, %s, %s)",
                           (user_id, item_id, start_date))
            booking_id = cursor.lastrowid  # ID der neuen Buchung abrufen

            # Status des Fahrzeugs auf 'vermietet' aktualisieren
            cursor.execute("UPDATE item SET status = 'vermietet' WHERE id = %s", (item_id,))
            conn.commit()
            return jsonify({"message": "Buchung erfolgreich.", "booking_id": booking_id}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Buchung: {err}"}), 500

    finally:
        conn.close()

@app.route("/return", methods=["POST"])
def return_item():
    """
    Handhabt die Rückgabe eines Fahrzeugs.
    :return: JSON-Antwort mit Erfolgsmeldung oder Fehler.
    """
    data = request.json
    booking_id = data.get("booking_id")
    location = data.get("location")

    # Überprüfen, ob Buchungs-ID und Standort angegeben wurden
    if not booking_id:
        return jsonify({"error": "Buchungs-ID ist erforderlich."}), 400
    if not location:
        return jsonify({"error": "Standort ist erforderlich."}), 400

    conn = db_connection()
    if isinstance(conn, tuple):  # Wenn ein Fehler aufgetreten ist
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        # Überprüfen, ob die Buchung existiert
        cursor.execute("SELECT * FROM booking WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({"error": "Die Buchung wurde nicht gefunden."}), 400

        # Fahrzeug zurückgeben
        cursor.execute("UPDATE item SET status = 'verfügbar', location = %s WHERE id = %s",
                       (location, booking["item_id"]))
        cursor.execute("DELETE FROM booking WHERE id = %s", (booking_id,))
        conn.commit()
        return jsonify({"message": "Fahrzeug erfolgreich zurückgegeben.", "redirect": "buchung.html"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Rückgabe: {err}"}), 500

    finally:
        conn.close()

@app.route("/overview", methods=["GET"])
def overview():
    """
    Gibt eine Übersicht aller Mietvorgänge zurück.
    :return: JSON-Antwort mit den Buchungsdaten.
    """
    conn = db_connection()
    if isinstance(conn, tuple):  # Wenn ein Fehler aufgetreten ist
        return conn

    cursor = conn.cursor(dictionary=True)

    try:
        # Alle Buchungen abrufen
        cursor.execute("""
            SELECT u.personal_number, b.start_date, b.end_date, i.id AS item_id, i.type, i.location
            FROM booking b
            JOIN user u ON b.user_id = u.id
            JOIN item i ON b.item_id = i.id
        """)
        bookings = cursor.fetchall()
        return jsonify(bookings), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Datenbankfehler bei der Abfrage der Übersicht: {err}"}), 500

    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)