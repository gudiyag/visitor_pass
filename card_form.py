# from flask import Flask, render_template, request
# from pymongo import MongoClient
# import os

# app = Flask(__name__)
# client = MongoClient(os.getenv('MONGO_URI'))
# db = client["visitor_pass"]

# @app.route("/aadhaar_details", methods=["GET", "POST"])
# def aadhaar_details():
#     if request.method == "POST":
#         aadhaar_number = request.form.get("aadhaar_number")
#         full_name = request.form.get("full_name")
#         dob = request.form.get("dob")
#         gender = request.form.get("gender")
#         # address = request.form.get("address")


#         db.aadhaar_card_details.insert_one({
#             "aadhaar_number": aadhaar_number,
#             "full_name":full_name, 
#             "dob":dob, 
#             "gender": gender,
#             # "address": address
#         })
#     return render_template('aadhaar_form.html')  


# @app.route("/pan_details", methods=["GET", "POST"])
# def pan_details():
#     if request.method == "POST":
#         pan_number = request.form.get("pan_number")
#         full_name = request.form.get("full_name")
#         father_name = request.form.get("father_name")
#         dob = request.form.get("dob")


#         db.pan_card_details.insert_one({
#             "pan_number": pan_number,
#             "full_name": full_name,
#             "father_name": father_name,
#             "dob": dob,
#         })
#     return render_template('pan_form.html') 

# if __name__ == "__main__":
#     app.run(debug=True)
