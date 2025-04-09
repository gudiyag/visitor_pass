# from app import db

# class AuthService:
#     def register(self, user_name,email,password,cpassword):
#         existing_user = db.user.find_one({"email": email})
#         if existing_user:
#             flash("User already registered!", "danger")
#             return ""

#         if password != cpassword:
#             flash("Password did not match", "danger")
#             return redirect(url_for("register"))
        
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

#         db.user.insert_one({
#             "user_name":user_name, 
#             "email":email, 
#             "password": hashed_password
#         })
       