# from flask import Flask, Response, render_template, redirect,send_from_directory
# import cv2
# import os
# from datetime import datetime

# app = Flask(__name__)

# # Define the path to save images
# UPLOAD_FOLDER = os.path.join('static', 'captured_image')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # Ensure the directory exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# image_filename = None  # Store latest captured image filename
# cap=None

# # generate_frames-------------
# def generate_frames():
#     global cap
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Open the camera

#     while True:
#         success, frame = cap.read()  # Read frames
#         if not success:
#             break

#         _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Streaming response format

#     cap.release()
    
    
# # home page----------------
# @app.route("/")
# def index():            
#     return render_template("open_cam.html")

# # capture video feed-------
# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # start camera-----------
# @app.route('/open_camera', methods=["POST"])
# def open_camera():
#     return render_template("live_cam_feed.html")


# # stop camera------
# @app.route("/stop_camera", methods=["GET","POST"])
# def stop_camera():
#     cap.release()
#     cv2.destroyAllWindows()
#     return redirect("/")

# # Capture Image (Stores it in memory)
# @app.route('/capture')
# def capture():
#     global captured_frame
#     success, frame = cap.read()
#     if success:
#         current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"captured_image_{current_time}.jpg"
#         img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)    
#         # Save the image using OpenCV
#         cv2.imwrite(img_path, frame)
#         return filename 
        
#     return "Error capturing image", 500

# @app.route('/static/<filename>')
# def get_image(filename):
#     return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)  


# if __name__ == '__main__':
#     app.run(debug=True,port=5000)
