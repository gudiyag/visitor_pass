# import pytesseract
# from PIL import Image
# import cv2
# import os
# import re

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# def convert_image_to_text(image_path):
#     # Read the image using OpenCV
#     img = cv2.imread(image_path)

#     # Check if the image is loaded correctly
#     if img is None:
#         raise ValueError(f"Error: Image not found at path {image_path}")
    
#     # Convert the image to grayscale (optional, but often helps OCR accuracy)
#     gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Use pytesseract to extract text from the imagesaxs
#     extracted_text = pytesseract.image_to_string(gray_img)
#     #print(extracted_text)
#     return extracted_text


# def parse_aadhaar_details(text):
#     adhaar_number = re.search(r"\d{4} \d{4} \d{4}", text)
#     name_match = re.search(r"(?i)(?:Name|नाम):?\s*(.*)", text)
#     dob_match = re.search(r"(?i)(?:DOB|Date\s*of\s*Birth|जन्म\s*तिथि)[^\d]{0,10}(\d{2}/\d{2}/\d{4})", text)
#     gender_match = re.search(r"(?i)(?:Male|Female|Transgender|पुरुष|महिला)", text)

#     return {
#         "adhaar_number": adhaar_number.group(0) if adhaar_number else None,
#         "full_name": name_match.group(1) if name_match else None,
#         "dob": dob_match.group(1) if dob_match else None,
#         "gender": gender_match.group(0) if gender_match else None,
#         "address": None  
#     }


# def parse_pan_details(text):
#     print(f"pan details : {text}")

#     pan_number = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
#     name_match = re.search(r"(?i)(?:Name|नाम):?\s*(.*)", text)
#     father_match = re.search(r"(?i)(?:Father's Name|पिता का नाम):?\s*(.*)", text)
#     dob_match = re.search(r"(?i)(?:DOB|Date\s*of\s*Birth|जन्म\s*तिथि|जन्म\s*की\s*तारीख)[^\d]{0,10}(\d{2}/\d{2}/\d{4})", text)

#     # issued_by_match = re.search(r"(?i)(?:Issued By|जारीकर्ता):?\s*(.*)", text)

#     return {
#         "pan_number": pan_number.group(0) if pan_number else None,
#         "full_name": name_match.group(1) if name_match else None,
#         "father_name": father_match.group(1) if father_match else None,
#         "dob": dob_match.group(1) if dob_match else None,
#         # "issued_by": issued_by_match.group(1) if issued_by_match else "Income Tax Department"
#     }


# pan_img_path = (r"static/css/imgs/pan.jpg")  
# adhaar_img_path = (r"static/css/imgs/adharcard.jpg")


# # Check if file exists before processing
# if os.path.exists(pan_img_path):
#     text = convert_image_to_text(pan_img_path)
#     text2 = convert_image_to_text(adhaar_img_path)
#     #print("Extracted Text:\n", text)
#     print(parse_pan_details(text))
#     #print("Extracted Text:\n", text2)
#     print(parse_aadhaar_details(text2))

# else:
#     print(f"Error: File {pan_img_path} does not exist.")
