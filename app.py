import streamlit as st
import pandas as pd
import io
from PIL import Image
import google.generativeai as genai

st.set_page_config(page_title="Passport to Excel", page_icon="📄", layout="wide")

st.title("📄 Passport & ID to Excel Generator")
st.write("อัปโหลดรูปภาพหนังสือเดินทางหรือบัตรประชาชน เพื่อแปลงข้อมูลเป็นไฟล์ Excel")

api_key = st.sidebar.text_input("ใส่ Gemini API Key ของคุณ:", type="password")

if api_key:
    genai.configure(api_key=api_key)

uploaded_files = st.file_uploader("เลือกรูปภาพ (รองรับหลายรูปพร้อมกัน)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files and api_key:
    if st.button("🚀 สแกนรูปภาพและสร้างตาราง Excel"):
        results = []
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        with st.spinner("กำลังประมวลผลรูปภาพ..."):
            for idx, uploaded_file in enumerate(uploaded_files, start=1):
                image = Image.open(uploaded_file)
                prompt = """
                Extract data from this document into JSON format with keys:
                - surname
                - given_names
                - doc_number
                - dob
                - sex
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    # Parse simplified mock structure for demonstration
                    results.append({
                        "ลำดับ (No.)": idx,
                        "นามสกุล (Surname)": "Extracted Data",
                        "ชื่อ (Given Names)": uploaded_file.name,
                        "เลขเอกสาร (ID / Passport No.)": "-",
                        "วันเกิด (Date of Birth)": "-",
                        "เพศ (Sex)": "-"
                    })
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดกับไฟล์ {uploaded_file.name}: {e}")
        
        if results:
            df = pd.DataFrame(results)
            st.success("ประมวลผลเสร็จสิ้น!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel",
                data=processed_data,
                file_name="passport_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
elif not api_key:
    st.info("💡 กรุณากรอง Gemini API Key ที่แถบเมนูด้านซ้ายก่อนเริ่มต้นใช้งาน")
