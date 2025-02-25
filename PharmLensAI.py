
import streamlit as st
import google.generativeai as genai
from google.generativeai import types
import time
import easyocr
import numpy as np
import cv2
from PIL import Image
from fpdf import FPDF


genai.configure(api_key="AIzaSyAKVvy0pSvo_uYQslHbvtDat_t3fPyULiI")
responseimage=""
def get_medical_advice(symptoms, age, allergies, medications,image):
    model = genai.GenerativeModel("gemini-2.0-flash")
    if ({symptoms}==""):
        return "No symptoms provided. Please provide symptoms to receive medical advice."
    else:

        prompt = (f"You are an AI medical assistant.Keep the output strictly about the below mentioned prompts.Based on the provided symptoms, age, allergies, medications, and prescription (if available), give structured medical advice. Keep it clear, professional, and easy to understand. Use this format:\n\n"
              "Possible Diagnosis: (List likely conditions)\n"
              "Recommended Medications: (Include OTC and prescription options if relevant)\n"
              "Precautions & Warnings: (Who should avoid these medications and possible side effects)\n"
              "Home Remedies & Lifestyle Tips: (If applicable)\n"
              "When to See a Doctor: (Serious signs that need urgent care)\n\n"
              "Patient Details:\n"
              f"Symptoms: {symptoms}\n"
              f"Age: {age}\n"
              f"Allergies: {allergies}\n"
              f"Current Medications: {medications}\n"
              f"Prescription (if provided): {image}\n\n"
              "Important:\n"
              "If no clear symptoms or prescription details are given, state that a doctors consultation is necessary.\n"
              " Ensure accuracy and avoid making assumptions.")
    response = model.generate_content([prompt,responseimage])
    return response.text

def extract_text_from_image(image):
    reader = easyocr.Reader(['en'])
    img_array = np.array(image.convert('RGB'))
    img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    _, img_thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    result = reader.readtext(img_thresh, detail=1)
    extracted_text = " ".join([text for (_, text, conf) in result if conf > 0.5])
    return extracted_text if extracted_text else "⚠️ Unable to extract clear text. Try another image."



responseimage=""

def analyze_image_with_gemini(image):
   genai.configure(api_key="AIzaSyAKVvy0pSvo_uYQslHbvtDat_t3fPyULiI")

def analyze_image_with_gemini(image):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = "What is this image give me strictly in points only the ones related to medicine and medical background?"
    responseimage = model.generate_content([prompt, image])
    return responseimage.text

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774290.png", width=120)
    st.title("🔍 AI Pharma Assistant")
    st.write("Upload a prescription or describe symptoms to get medical recommendations.")
   
st.title("🩺 AI Pharmacist Assistant")
st.write("Upload a prescription image or manually enter symptoms to get AI-powered guidance.")


uploaded_image = st.file_uploader("📄 Upload a handwritten prescription (optional)", type=["png", "jpg", "jpeg"])
extracted_text = ""

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Prescription", use_container_width=True)
    extracted_text = extract_text_from_image(image)
    st.write("✍️ Extracted Text:", extracted_text)
    
   
    with st.spinner("🔍 Analyzing Image..."):
        image_analysis = analyze_image_with_gemini(image)
        st.write("🤖 Prescription Generation:")
        st.markdown(image_analysis)

name=st.text_area("👨Enter Your Name")
symptoms = st.text_area("🩺 Enter your symptoms:",)
age = st.number_input("🎂 Enter your age:", min_value=0, max_value=120)
allergies = st.text_input("🚫 List any known allergies:", "None")
medications = st.text_input("💊 List any current medications:", "None")



def convert_markdown_to_text_with_ai(markdown_text):
    """Uses Gemini 2.0 Flash to convert Markdown-formatted text to plain text."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Convert the following Markdown text to plain, well-structured text while preserving the meaning:
    ```markdown
    {markdown_text}
    ```
    Remove any unnecessary symbols like **, *, #, [], (), and format it into readable sentences.
    make sure that the word limit is 100-200 words only and all the data is properly written as pointers.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_pdf_report(patient_name, age, symptoms, advice):
    """Generates a well-formatted PDF report with AI-converted plain text advice."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Medical Advice Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Times", style='BU', size=14)
    pdf.cell(0, 10, "Patient Details:", ln=True)
    pdf.set_font("Courier", style='B', size=12)
    pdf.cell(0, 10, f"Name: {patient_name}", ln=True)
    pdf.cell(0, 10, f"Age: {age}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", style='BI', size=12)
    pdf.cell(0, 10, "Symptoms:", ln=True)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, symptoms)
    pdf.ln(5)

    pdf.set_font("Arial", style='BU', size=12)
    pdf.cell(0, 10, "AI Advice:", ln=True)
    pdf.set_font("Arial", size=12)

    plain_text_advice = convert_markdown_to_text_with_ai(advice)  
    pdf.multi_cell(0, 10, plain_text_advice)

    pdf_file = "medical_advice.pdf"
    pdf.output(pdf_file)
    return pdf_file

if st.button("💡 Get AI Medical Advice"):
    if not symptoms.strip():
        st.warning("⚠️ Please enter symptoms to receive medical advice.")
    else:
        with st.spinner("🔄 Processing your request..."):
            time.sleep(2)
            ai_advice = get_medical_advice(symptoms, age, allergies, medications,responseimage)
            st.write("## 🤖 AI-Powered Medical Advice")
            st.markdown(ai_advice)

            # PDF Report
            pdf_file = generate_pdf_report(name, age, symptoms, ai_advice)
            with open(pdf_file, "rb") as pdf:
                st.download_button(label="📄 Download Report", data=pdf, file_name="Medical_Report.pdf", mime="application/pdf")
