
# beautesis_sustainability_app.py
import streamlit as st
import pandas as pd
import io
from PyPDF2 import PdfReader

st.set_page_config(page_title="Beautesis Sustainability Scorer", layout="wide")
st.title("🌿 Beautesis Sustainable Formulation Index (SFI)")
st.markdown("Choose how you want to input your formulation:")

mode = st.radio("Input mode", ["📄 Upload file", "✏️ Paste formulation manually"])

df = None

if mode == "📄 Upload file":
    uploaded_file = st.file_uploader("Upload a .csv, .xlsx, or .pdf", type=["csv", "xlsx", "pdf"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                rows = [line for line in text.split("\n") if "," in line]
                data = [line.split(",") for line in rows]
                df = pd.DataFrame(data[1:], columns=data[0])
        except Exception as e:
            st.error(f"Error reading file: {e}")

elif mode == "✏️ Paste formulation manually":
    text_input = st.text_area("Paste your INCI list (comma-separated: Ingredient,Function,%, etc.)")
    if text_input:
        try:
            lines = [l for l in text_input.split("\n") if "," in l]
            data = [line.split(",") for line in lines]
            df = pd.DataFrame(data[1:], columns=data[0])
        except Exception as e:
            st.error(f"Error parsing text: {e}")

if df is not None:
    st.success("✅ Formulation parsed successfully!")
    st.dataframe(df)

    score = 0
    total = 100
    advisory = []

    if "INCI" in df.columns:
        noi_criteria = any("hyaluronate" in str(i).lower() or "natural" in str(i).lower() for i in df["INCI"])
        if noi_criteria:
            score += 10
        else:
            advisory.append("Increase natural or biobased ingredients to improve NOI.")

        upcycled_or_biotech = any("ferment" in str(i).lower() or "biotech" in str(i).lower() for i in df["INCI"])
        if upcycled_or_biotech:
            score += 5
        else:
            advisory.append("Use biotech or upcycled ingredients.")

        petrochemicals = any("PEG" in str(i) or "dimethicone" in str(i).lower() for i in df["INCI"])
        if not petrochemicals:
            score += 10
        else:
            advisory.append("Reduce PEGs and silicones.")

    if "Wt %" in df.columns:
        try:
            wt_series = df["Wt %"].astype(str).str.replace("%", "").str.strip()
            wt_floats = pd.to_numeric(wt_series, errors="coerce")
            if wt_floats.lt(2).sum() > 5:
                score += 5
            else:
                advisory.append("Use more high-efficiency actives (<2%).")
        except:
            advisory.append("Could not evaluate usage percentages.")

    score += 5
    advisory.append("Specify eco-packaging format for extra score.")

    if "Function" in df.columns:
        keywords = ["brightening", "hydrating", "fast", "multifunction", "barrier", "sensorial"]
        if any(any(k in str(f).lower() for k in keywords) for f in df["Function"]):
            score += 15
        else:
            advisory.append("Add wellness or multifunctional claims.")

    if score >= 80:
        badge = "💚 Sustainably Formulated"
    elif score >= 60:
        badge = "💛 Better Choice"
    else:
        badge = "⚠️ Needs Improvement"

    st.markdown("---")
    st.subheader("📊 Sustainability Score")
    st.metric("SFI Score", f"{score} / {total}")
    st.success(f"Rating: {badge}")

    st.markdown("---")
    st.subheader("📝 Advisory Feedback")
    for point in advisory:
        st.write("- ", point)

    if st.button("✅ Approve & Export to CRM"):
        st.success("Formulation score and feedback approved and ready for CRM integration.")
