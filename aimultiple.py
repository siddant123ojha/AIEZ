import streamlit as st
import datetime
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

# ✅ Secure API key from Streamlit secrets
api_key = st.secrets["GEMINI_apikey"]

# ✅ Create client with latest SDK
client = genai.Client(api_key=api_key)
models = client.models

# Streamlit page config
st.set_page_config(page_title="Multi-AI App (Latest SDK)", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

page = st.sidebar.radio("Select Feature:", ["Teaching", "Image Generator", "Math Solver", "History"])

# ---------------- Teaching Assistant ---------------- #
def run_teaching_assistant():
    st.header("📘 AI Teaching Assistant")
    prompt = st.text_area("Ask your question:", height=150)
    if st.button("Get Answer"):
        if prompt.strip():
            with st.spinner("Generating..."):
                resp = models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt.strip()
                )
                st.write(resp.text)
                st.session_state.history.append(("Text", prompt.strip(), resp.text))
        else:
            st.warning("Please enter something.")

# ---------------- Image Generator ---------------- #
def run_image_generator():
    st.header("🖼️ Safe AI Image Generator")
    prompt = st.text_area("Describe the image:", height=150)
    if st.button("Generate Image"):
        if prompt.strip():
            with st.spinner("Generating image..."):
                resp = models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=[types.Content(role="user", parts=[types.Part(text=prompt.strip())])],
                    config=types.GenerateContentConfig(
                        response_modalities=[types.Modality.TEXT, types.Modality.IMAGE]
                    )
                )
                parts = resp.candidates[0].content.parts
                img_data = next((p.inline_data.data for p in parts if p.inline_data and p.inline_data.data), None)
                if img_data:
                    img = Image.open(BytesIO(img_data))
                    st.image(img, use_container_width=True)
                    fn = f"img_{datetime.datetime.now():%Y%m%d%H%M%S}.png"
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("Download Image", buf.getvalue(), file_name=fn, mime="image/png")
                    st.session_state.history.append(("Image", prompt.strip(), fn))
                else:
                    st.error("No image returned.")
        else:
            st.warning("Enter a prompt.")

# ---------------- Math Solver ---------------- #
def run_math_mastermind():
    st.header("🧠 Math Mastermind")
    q = st.text_area("Enter a math problem:", height=150)
    if st.button("Solve"):
        if q.strip():
            with st.spinner("Solving..."):
                resp = models.generate_content(
                    model="gemini-2.0-flash",
                    contents=q.strip()
                )
                st.write(resp.text)
                st.session_state.history.append(("Math", q.strip(), resp.text))
        else:
            st.warning("Please enter a math problem.")

# ---------------- History Log ---------------- #
def run_history_log():
    st.header("📜 History")
    if not st.session_state.history:
        st.info("No interactions yet.")
        return
    for idx, (mode, prompt, out) in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{mode} #{idx}"):
            st.write("**Prompt:**", prompt)
            st.write("**Output:**", out)

# ---------------- Page Routing ---------------- #
if page == "Teaching":
    run_teaching_assistant()
elif page == "Image Generator":
    run_image_generator()
elif page == "Math Solver":
    run_math_mastermind()
else:
    run_history_log()
