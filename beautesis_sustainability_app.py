
# beautesis_sustainability_app.py v3
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

st.set_page_config(page_title="Beautesis SFI AI Parser", layout="wide")
st.title("🌿 Beautesis Sustainable Formulation Index")
st.markdown("Upload a full formulation PDF. We'll extract, score, and guide.")

uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def estimate_score(text):
    score_data = []

    # Ingredient profile
    score = 0
    comments = []
    if "hyaluronate" in text.lower() or "niacinamide" in text.lower():
        score += 10
    else:
        comments.append("Consider using well-known natural actives like HA or vitamins.")
    if "PEG" not in text and "dimethicone" not in text.lower():
        score += 10
    else:
        comments.append("Try reducing PEGs or silicones.")
    if "upcycled" in text.lower() or "biotech" in text.lower():
        score += 5
    else:
        comments.append("No mention of upcycled/biotech sources.")
    score_data.append(("Ingredient profile", score, 30, comments))

    # Formulation impact
    score = 0
    comments = []
    if "cold process" in text.lower():
        score += 10
    else:
        comments.append("Cold process not specified.")
    if "usage rate" in text.lower() or "<2%" in text:
        score += 5
    if "waterless" in text.lower():
        score += 10
    else:
        comments.append("Waterless or concentrated format not found.")
    score_data.append(("Formulation impact", score, 25, comments))

    # Packaging/format
    score = 0
    comments = []
    if "stick" in text.lower() or "solid" in text.lower():
        score += 10
    if "refill" in text.lower() or "recyclable" in text.lower():
        score += 5
    else:
        comments.append("Packaging or eco-format not identified.")
    score_data.append(("Packaging", score, 20, comments))

    # Application relevance
    score = 0
    comments = []
    keywords = ["hydrating", "brightening", "barrier", "fast-acting", "sensorial", "multi"]
    matches = [k for k in keywords if k in text.lower()]
    score += min(25, len(matches) * 5)
    if not matches:
        comments.append("No clear consumer-facing claims found.")
    score_data.append(("Application relevance", score, 25, comments))

    return score_data

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Text extracted from PDF.")
    with st.expander("📝 Raw Extracted Text"):
        st.write(text)

    results = estimate_score(text)

    st.subheader("📊 Sustainability Score Breakdown")
    total = 0
    max_total = 0
    for cat, val, maxval, comments in results:
        total += val
        max_total += maxval
        st.markdown(f"**{cat}:** {val} / {maxval}")
        for c in comments:
            st.write("•", c)

    st.markdown("---")
    st.metric("🌟 Final Score", f"{total} / {max_total}")
    if total >= 80:
        st.success("💚 Sustainably Formulated")
    elif total >= 60:
        st.info("💛 Better Choice")
    else:
        st.warning("⚠️ Needs Improvement")
