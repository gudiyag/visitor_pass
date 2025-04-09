from flask import Flask, render_template, request, redirect, url_for, flash, Response, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson import ObjectId       
import os
import pytesseract
from PIL import Image
import cv2
import re
from datetime import datetime
import time



app = Flask(__name__)
app.secret_key = "secret123"

login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)

client = MongoClient(os.getenv('MONGO_URI'))
db = client["visitor_pass"]



# User Model for login
class User(UserMixin):
    def __init__(self, user_id, username, email, password):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = db.user.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(str(user_data["_id"]), user_data["user_name"], user_data["email"], user_data["password"])
    except:
        return None
    return None


@app.route("/")
def test():
    return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")

        existing_user = db.user.find_one({"email": email})

        if existing_user:
            flash("User already registered!", "danger")
            return redirect(url_for("register"))

        if password != cpassword:
            flash("Password did not match", "danger")
            return redirect(url_for("register"))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
 
        db.user.insert_one({
            "user_name":user_name, 
            "email":email, 
            "password": hashed_password
        })

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_data = db.user.find_one({"email": email})
        if user_data and bcrypt.check_password_hash(user_data["password"], password):
            user = User(str(user_data["_id"]), user_data["user_name"], user_data["email"], user_data["password"])
            login_user(user)

            # role = user_data.get("role","")

            return redirect(url_for("home_dash"))

            # if role == "admin":
            #     return redirect(url_for('security_dashboard'))
            # elif role == "super admin":
            #     return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid email or password", "danger")
            
    return render_template("login.html")


# @app.route("/security_dashboard")
# @login_required
# def security_dashboard():   
#     return render_template("security_dashboard.html", username=current_user.username)


# @app.route("/admin_dashoard")
# @login_required
# def admin_dashboard():
#     return render_template("admin_dashboard.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logout!", "info")
    return redirect(url_for("login"))



#---------------------------------------------- Camera Feature ------------------------------------------------------


# Define the path to save images
UPLOAD_FOLDER = os.path.join('static', 'captured_images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
image_filename = None  # Store latest captured image filename
cap=None

# generate_frames-------------
def generate_frames():
    global cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Open the camera

    while True:
        success, frame = cap.read()  # Read frames
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Streaming response format

    cap.release()
    

# camera page----------------
@app.route("/camera")
def camera():            
    return render_template("open_cam.html")

# capture video feed-------
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# start camera-----------
@app.route('/open_camera', methods=["POST"])
def open_camera():
    return render_template("live_cam_feed.html")


# stop camera------
@app.route("/stop_camera", methods=["GET","POST"])
def stop_camera():
    cap.release()
    cv2.destroyAllWindows()
    return redirect("extract_details")

# Capture Image (Stores it in memory)
@app.route('/capture')
def capture():
    global captured_frame
    success, frame = cap.read()
    if success:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"captured_image_{current_time}.jpg"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)    
        # Save the image using OpenCV
        cv2.imwrite(img_path, frame)
        return filename 
        
    return "Error capturing image", 500

@app.route('/static/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)  



#------------------------------------ code for extracting details from cards and saving to database --------------------------------------


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def convert_image_to_text(image_path):
    # Read the image using OpenCV
    img = cv2.imread(image_path)

    # Check if the image is loaded correctly
    if img is None:
        raise ValueError(f"Error: Image not found at path {image_path}")
    
    # Convert image to grayscale for better OCR accuracy
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract text from the imagesaxs
    extracted_text = pytesseract.image_to_string(gray_img)
    return extracted_text


def parse_aadhaar_details(text):
    aadhaar_number = re.search(r"\d{4} \d{4} \d{4}", text)
    name_match = re.search(r"(?i)(?:Name|नाम):?\s*(.*)", text)
    dob_match = re.search(r"(?i)(?:DOB|Date\s*of\s*Birth|जन्म\s*तिथि)[^\d]{0,10}(\d{2}/\d{2}/\d{4})", text)
    gender_match = re.search(r"(?i)(?:Male|Female|Transgender|पुरुष|महिला)", text)

    return{
        "aadhaar_number": aadhaar_number.group(0) if aadhaar_number else None,
        "full_name": name_match.group(1) if name_match else None,
        "dob": dob_match.group(1) if dob_match else None,
        "gender": gender_match.group(0) if gender_match else None
    }
    # return


def parse_pan_details(text):
    pan_number = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
    name_match = re.search(r"(?i)(?:Name|नाम):?\s*(.*)", text)
    father_match = re.search(r"(?i)(?:Father's Name|पिता का नाम):?\s*(.*)", text)
    dob_match = re.search(r"(?i)(?:DOB|Date\s*of\s*Birth|जन्म\s*तिथि|जन्म\s*की\s*तारीख)[^\d]{0,10}(\d{2}/\d{2}/\d{4})", text)


    return {
        "pan_number": pan_number.group(0) if pan_number else None,
        "full_name": name_match.group(1) if name_match else None,
        "father_name": father_match.group(1) if father_match else None,
        "dob": dob_match.group(1) if dob_match else None
    }


@app.route("/extract_details", methods=["GET", "POST"])
def extract_details():
    img_path = "static/captured_images"

    if os.path.exists(img_path):
        image_files = [os.path.join(img_path, f) for f in os.listdir(img_path) if f.lower().endswith(('.jpg'))]
        
        if image_files:
            latest_image = max(image_files, key=os.path.getmtime)
            extracted_text = convert_image_to_text(latest_image)

            if not extracted_text:
                return "No text detected. Try again with a clearer image.", 400

            aadhaar_number = re.search(r"\d{4} \d{4} \d{4}", extracted_text)
            pan_number = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", extracted_text)
            
            if aadhaar_number:
                return redirect(url_for("aadhaar_details"))
            elif pan_number:
                return redirect(url_for("pan_details"))
            
    return "Document type could not be determined.", 400

@app.route("/aadhaar_details", methods=["GET", "POST"])
def aadhaar_details():
    aadhaar_img_path = "static/captured_images"
    aadhaar_data = {}

    if os.path.exists(aadhaar_img_path):
        image_files = [os.path.join(aadhaar_img_path, f) for f in os.listdir(aadhaar_img_path) if f.lower().endswith(('.jpg'))]

        if image_files:
            latest_image = max(image_files, key=os.path.getmtime)  # Get the most recently modified image
                
            aadhaar_text = convert_image_to_text(latest_image)
            aadhaar_data = parse_aadhaar_details(aadhaar_text)
        
    #----------------- saving extracted data into db ----------------------
    if request.method == "POST":
        aadhaar_number = request.form.get("aadhaar_number")
        full_name = request.form.get("full_name")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        father_name = request.form.get("father_name")
        card = request.form.get("card")
        issue_date = request.form.get("issue_date")
        purpose = request.form.get("purpose")

        db.aadhaar_card_details.insert_one({
            "aadhaar_number": aadhaar_number,
            "full_name":full_name, 
            "dob":dob, 
            "gender": gender,
            "father_name": father_name,
            "card": card,
            "issue_date": issue_date,
            "purpose": purpose,
        })
        return redirect(url_for("home_dash"))

    return render_template("aadhaar_details.html", aadhaar=aadhaar_data)


@app.route("/pan_details", methods=["GET", "POST"])
def pan_details():
    pan_img_path = "static/captured_images"
    pan_data = {}

    if os.path.exists(pan_img_path):
        image_files = [os.path.join(pan_img_path, f) for f in os.listdir(pan_img_path) if f.lower().endswith(('.jpg'))]

        if image_files:
            latest_image = max(image_files, key=os.path.getmtime)  # Get the most recently modified image
            pan_text = convert_image_to_text(latest_image)
            pan_data = parse_pan_details(pan_text)
    
    #----------------- saving extracted data into db ----------------------
    if request.method == "POST":
        pan_number = request.form.get("pan_number")
        full_name = request.form.get("full_name")
        father_name = request.form.get("father_name")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        card = request.form.get("Card")
        issue_date = request.form.get("Issue_date")
        purpose = request.form.get("Purpose")

        db.pan_card_details.insert_one({
            "pan_number": pan_number,
            "full_name": full_name,
            "father_name": father_name,
            "dob": dob,
            "gender": gender,
            "card": card,
            "issue_date": issue_date,
            "purpose": purpose,
        })
        return redirect(url_for("home_dash"))
    
    return render_template("pan_details.html", pan=pan_data)


#------------------------------------------------ Dashboard Routes and logics -----------------------------------------------


@app.route("/home_dash")
@login_required
def home_dash():
    return render_template("home_dashboard.html")


# @app.route("/visitorOverview_dash")
# @login_required
# def visitorOverview_dash():
#     return render_template("visitorOverview_dashboard.html")


@app.route("/userOverview_dash")
@login_required
def userOverview_dash():
  

    return render_template("userOverview_dashboard.html",)


@app.route("/all_visitor")
@login_required
def all_visitor():
    data =list(db.pan_card_details.find())or list(db.aadhaar_card_details.find())
    # data2 =list(db.aadhaar_card_details.find())


    return render_template("all_visitor.html", pan_data=data)


@app.route("/accepted_visitor")
@login_required
def accepted_visitor():
    data =list(db.pan_card_details.find({"isActive": "1"}))
    return render_template("accepted_visitor.html", pan_data=data)


# activate record--------
@app.route("/activate/<id>", methods=["GET"])
def activate(id):
    object_id = ObjectId(id)
    result = db.pan_card_details.update_one(
        {"_id": object_id}, 
        {"$set": {"isActive": "1"}} 
    )
    return redirect(url_for('all_visitor'))

# in-activate record--------
@app.route("/in-activate/<id>", methods=["GET"])
def in_activate(id):
    object_id = ObjectId(id)
    result = db.pan_card_details.update_one(
        {"_id": object_id}, 
        {"$set": {"isActive": "0"}} 
    )
    return redirect(url_for('all_visitor'))

@app.route("/rejected_visitor")
@login_required
def rejected_visitor():
    data =list(db.pan_card_details.find({"isActive": "0"}))
    return render_template("rejected_visitor.html",pan_data=data)



if __name__ == "__main__":
    app.run(debug=True)
