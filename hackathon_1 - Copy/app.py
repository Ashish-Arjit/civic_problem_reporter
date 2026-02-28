import os
import uuid
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv() # Load variables from .env if present

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# MySQL Connection Details
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root@#0987'),
    'database': os.getenv('DB_NAME', 'hackathon_db')
}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_all_complaints', methods=['GET'])
def get_all_complaints():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Order by created_at descending to show newest first
        cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC")
        complaints = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(complaints)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({"error": "Resource not found", "description": str(e)}), 404

@app.route('/health', methods=['GET'])
@app.route('/api/status', methods=['GET'])
def health():
    return jsonify({"status": "OK"})

@app.route('/submit', methods=['POST'])
def submit_complaint():
    try:
        # Get form data
        username = request.form.get('username')
        phone = request.form.get('phone')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        priority = request.form.get('priority')
        preferred_platform = request.form.get('preferred_platform', 'Twitter')

        # Basic Validation
        if not all([username, phone, latitude, longitude, priority]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            lat = float(latitude)
            lng = float(longitude)
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid GPS coordinates"}), 400

        if priority not in ['Low', 'Medium', 'High', 'Critical']:
            return jsonify({"error": "Invalid priority level"}), 400
            
        if preferred_platform not in ['Twitter', 'Facebook', 'Instagram']:
            return jsonify({"error": "Invalid social platform choice"}), 400

        # File Handling
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4()}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                image_path = save_path

        # Database Insertion
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO complaints (username, phone, latitude, longitude, priority, image_path, preferred_platform)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, phone, lat, lng, priority, image_path, preferred_platform))
        complaint_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "id": complaint_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/simulate_social_login', methods=['POST'])
def simulate_social_login():
    """
    Hackathon Utility: Simulates logging into a social media platform.
    Accepts any username/password for demo simplicity.
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        platform = data.get('platform')

        if not all([username, password, platform]):
            return jsonify({"error": "Missing credentials or platform"}), 400

        if platform not in ['Twitter', 'Facebook', 'Instagram']:
            return jsonify({"error": "Invalid platform"}), 400

        # Simulation: Always approve "login" for the hackathon
        return jsonify({
            "success": True, 
            "message": f"Successfully logged into {platform} as @{username}. Session linked for escalation."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_pending', methods=['GET'])
def check_pending():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Find complaints: status='Pending' AND created_at < NOW() - 48 HOURS
        query = """
            SELECT * FROM complaints 
            WHERE status = 'Pending' 
            AND created_at < (NOW() - INTERVAL 48 HOUR)
        """
        cursor.execute(query)
        overdue_complaints = cursor.fetchall()

        posted_count = 0
        for complaint in overdue_complaints:
            # Platform-Specific Simulation
            platform = complaint.get('preferred_platform', 'Twitter')
            comp_id = complaint['id']
            priority = complaint['priority']
            lat = complaint['latitude']
            lng = complaint['longitude']

            if platform == 'Twitter':
                tweet_text = f"🚨 URGENT: Complaint #{comp_id} ({priority} priority) at Lat:{lat}, Long:{lng} has been PENDING for over 48 hours! @CityAdmin #CivicFix"
                print(f"\n[TWITTER SIMULATION]\n{tweet_text}\n{'-'*30}")
            elif platform == 'Facebook':
                fb_text = f"CivicFix Community Alert: Complaint #{comp_id} ({priority} priority) remains unresolved for over 48 hours at Location: {lat}, {lng}. Please share to raise awareness! #CivicFix #CommunitySafety"
                print(f"\n[FACEBOOK SIMULATION]\n{fb_text}\n{'-'*30}")
            elif platform == 'Instagram':
                ig_caption = f"🚨 Accountability Check: Tracking Complaint #{comp_id} at {lat}, {lng}. Status: UNRESOLVED for 48+ hours. 🛑 #CivicFix #CityUpdate #Hackathon"
                print(f"\n[INSTAGRAM SIMULATION]\n{ig_caption}\n{'-'*30}")

            # Update status
            update_query = "UPDATE complaints SET status = 'Social_Notified' WHERE id = %s"
            cursor.execute(update_query, (comp_id,))
            posted_count += 1

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"overdue": len(overdue_complaints), "posted": posted_count})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/force_escalation', methods=['POST'])
def force_escalation():
    """
    Hackathon Utility: Manually backdates all 'Pending' complaints by 50 hours 
    so that /check_pending becomes active immediately.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "UPDATE complaints SET created_at = (NOW() - INTERVAL 50 HOUR) WHERE status = 'Pending'"
        cursor.execute(query)
        affected = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "backdated_count": affected, "message": "All pending complaints moved back 50 hours. Run /check_pending now!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mark_resolved/<int:complaint_id>', methods=['POST'])
def mark_resolved(complaint_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if complaint exists first
        cursor.execute("SELECT id, status FROM complaints WHERE id = %s", (complaint_id,))
        complaint = cursor.fetchone()
        
        if not complaint:
            cursor.close()
            conn.close()
            return jsonify({"error": "Complaint not found"}), 404
            
        # Update status (regardless of previous status for demo smoothness)
        query = "UPDATE complaints SET status = 'Resolved' WHERE id = %s"
        cursor.execute(query, (complaint_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": f"Complaint #{complaint_id} marked as resolved"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Startup Check: Verify MySQL is reachable
    print("\n[STARTUP] Checking MySQL connection...")
    try:
        test_conn = get_db_connection()
        test_conn.close()
        print("[SUCCESS] MySQL connected correctly.\n")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Could not connect to MySQL!")
        print(f"Check your connection details in app.py: root@localhost with password 'root@#0987'")
        print(f"Original Error: {str(e)}\n")
        # Exit if DB is not ready
        import sys
        sys.exit(1)

    app.run(debug=True, port=5050)
