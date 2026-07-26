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
        
        # เลือกโมเดลอัตโนมัติจากรายการที่ API Key นี้ใช้งานได้
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # เลือกโมเดล flash ตัวแรกที่พบ หรือใช้ตัวเริ่มต้น
            model_name = next((m for m in available_models if 'flash' in m), available_models[0] if available_models else 'gemini-1.5-flash')
            model = genai.GenerativeModel(model_name)
        except Exception as e:
            model = genai.GenerativeModel('gemini-1.5-flash')

        with st.spinner("กำลังประมวลผลรูปภาพ..."):
            for idx, uploaded_file in enumerate(uploaded_files, start=1):
                image = Image.open(uploaded_file)
                prompt = "Extract text data from this passport or ID card."
                
                try:
                    response = model.generate_content([prompt, image])
                    results.append({
                        "ลำดับ (No.)": idx,
                        "ชื่อไฟล์": uploaded_file.name,
                        "ข้อมูลที่สแกนได้": response.text
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
    st.info("💡 กรุณากรอก Gemini API Key ที่แถบเมนูด้านซ้ายก่อนเริ่มต้นใช้งาน")
