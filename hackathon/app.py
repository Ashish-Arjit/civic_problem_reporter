from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection(with_db=True):
    config = {
        "host": "localhost",
        "user": "root",
        "password": "root@#0987",
        "autocommit": True,
        "connection_timeout": 5
    }
    if with_db:
        config["database"] = "hackathon_db"
    return mysql.connector.connect(**config)

def init_db():
    try:
        print("Connecting to MySQL server...")
        # Connect without database to create it
        conn = get_db_connection(with_db=False)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS hackathon_db")
        cursor.close()
        conn.close()
        print("Database 'hackathon_db' verified/created.")

        # Connect to the database to create table
        conn = get_db_connection(with_db=True)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                phone VARCHAR(15),
                image_path VARCHAR(255),
                problem_description TEXT,
                address TEXT,
                latitude DOUBLE,
                longitude DOUBLE,
                priority VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.close()
        conn.close()
        print("Table 'complaints' verified/created.")
        print("Database initialized successfully.")
    except Exception as e:
        print(f"ERROR INITIALIZING DATABASE: {e}")
        print("The app will try to continue, but DB operations might fail.")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "ok", "message": "Backend is running!"})

@app.route("/submit", methods=["POST"])
def submit_problem():
    print("="*50)
    print("NEW SUBMISSION RECEIVED")
    
    username = request.form.get("username", "").strip()
    phone = request.form.get("phone", "").strip()
    description = request.form.get("description", "").strip()
    address = request.form.get("address", "").strip()
    latitude = request.form.get("latitude", "").strip()
    longitude = request.form.get("longitude", "").strip()
    priority = request.form.get("priority", "Medium")

    if not all([username, phone, description, address, latitude, longitude]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        lat = float(latitude)
        lon = float(longitude)
    except ValueError:
        return jsonify({"error": "Invalid GPS format"}), 400

    image_path = None
    image = request.files.get("image")
    if image and image.filename:
        if allowed_file(image.filename):
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO complaints 
        (username, phone, image_path, problem_description, address, latitude, longitude, priority)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (username, phone, image_path, description, address, lat, lon, priority))
        cursor.close()
        conn.close()
        return jsonify({"message": "Complaint submitted successfully"}), 201
    except Exception as e:
        print(f"DB INSERT ERROR: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

if __name__ == "__main__":
    print("Step 1: Starting Database Initialization...")
    init_db()
    print("Step 2: Starting Flask app on port 5001...")
    try:
        app.run(debug=True, host="0.0.0.0", port=5001)
    except Exception as e:
        print(f"FATAL ERROR STARTING SERVER: {e}")
