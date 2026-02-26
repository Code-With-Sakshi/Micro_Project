

from flask import Flask, request, jsonify
from flask_cors import CORS

# =========================
# DATABASE IMPORTS
# =========================
from mysql_db import get_db_connection
from certificate_db import get_certificate_connection

# USER DATABASE IMPORTS
from user_db import get_user_db_connection
from user_certificate import get_user_certificate_connection

import os
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# =====================================
# ADMIN SIGNUP API
# =====================================

@app.route("/api/admin/signup", methods=["POST"])
def admin_signup():
    try:
        data = request.json

        if not data:
            return jsonify({"status": "error", "msg": "No data received"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin_users WHERE official_email = %s",
            (data["official_email"],)
        )

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "msg": "Email already registered"})

        query = """
        INSERT INTO admin_users
        (org_name, org_type, official_email, contact_number, password, address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data["org_name"],
            data["org_type"],
            data["official_email"],
            data["contact_number"],
            data["password"],
            data["address"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "msg": "Signup Successful"})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


# =====================================
# ADMIN CERTIFICATE UPLOAD API
# =====================================

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/admin/certificate/upload", methods=["POST"])
def upload_certificate():
    try:
        recipient = request.form.get("recipient_name")
        certificate_id = request.form.get("certificate_id")
        issuer = request.form.get("issuer_name")
        course = request.form.get("course")
        issue_date = request.form.get("issue_date")
        file = request.files.get("certificate_file")

        if not file:
            return jsonify({"status": "error", "msg": "No file uploaded"})

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        file_hash = sha256.hexdigest()

        conn = get_certificate_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO certificates
        (recipient, certificate_id, issuer, course, issue_date, file_name, file_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            recipient,
            certificate_id,
            issuer,
            course,
            issue_date,
            filename,
            file_hash
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "msg": "Certificate uploaded successfully",
            "hash": file_hash
        })

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


# =====================================
# USER SIGNUP API
# =====================================

@app.route("/api/user/signup", methods=["POST"])
def user_signup():
    try:
        data = request.json

        if not data:
            return jsonify({"status": "error", "msg": "No data received"})

        conn = get_user_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (data["email"],))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "msg": "Email already exists"})

        query = """
        INSERT INTO users (full_name, email, phone, password)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (
            data["full_name"],
            data["email"],
            data["phone"],
            data["password"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "msg": "User Signup Successful"})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


# =====================================
# USER LOGIN API
# =====================================

@app.route("/api/user/login", methods=["POST"])
def user_login():
    try:
        data = request.json

        conn = get_user_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM users
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (data["email"], data["password"]))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return jsonify({"status": "success", "msg": "Login Successful"})
        else:
            return jsonify({"status": "error", "msg": "Invalid Credentials"})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


# =====================================
# USER CERTIFICATE UPLOAD API
# =====================================

USER_UPLOAD_FOLDER = "user_uploads"
os.makedirs(USER_UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/user/certificate/upload", methods=["POST"])
def user_certificate_upload():
    try:
        certificate_name = request.form.get("certificate_name")
        certificate_id = request.form.get("certificate_id")
        issue_date = request.form.get("issue_date")
        file = request.files.get("certificate_file")

        if not certificate_name or not certificate_id or not issue_date:
            return jsonify({"status": "error", "msg": "Missing required fields"})

        if not file:
            return jsonify({"status": "error", "msg": "No file uploaded"})

        filename = secure_filename(file.filename)
        file_path = os.path.join(USER_UPLOAD_FOLDER, filename)
        file.save(file_path)

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        file_hash = sha256.hexdigest()

        conn = get_user_certificate_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM user_certificates WHERE certificate_id = %s",
            (certificate_id,)
        )

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "msg": "Certificate ID already exists"})

        query = """
        INSERT INTO user_certificates
        (certificate_name, certificate_id, issue_date, file_name, file_hash)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            certificate_name,
            certificate_id,
            issue_date,
            filename,
            file_hash
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "msg": "User Certificate Uploaded Successfully",
            "hash": file_hash
        })

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


# =====================================
# RUN APP
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
