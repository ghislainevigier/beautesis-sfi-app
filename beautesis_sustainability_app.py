
# beautesis_sustainability_app.py v3.2
import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Beautesis SFI - AI + Manual Review", layout="wide")
st.title("🌿 Beautesis Sustainable Formulation Index")
st.markdown("Upload a formulation PDF. We'll auto-score and let you confirm or override with checkboxes.")

uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

def extract_text_from_pdf(uploaded_file):
    full_text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

def detect_flags(text):
    text = text.lower()
    return {
        "bio_based": any(w in text for w in ["botanical", "plant-based", "bio-based", "natural origin"]),
        "biotech": "biomimetic" in text or "ferment" in text or "biotech" in text,
        "upcycled": "upcycled" in text or "side stream" in text,
        "biodegradable": "biodegradable" in text,
        "no_peg": not any(w in text for w in ["peg", "dimethicone", "microplastic"]),
        "cold_process": "cold process" in text,
        "waterless": "waterless" in text or "solid stick" in text or "powder-to-foam" in text,
        "refillable": "refill" in text or "recyclable" in text or "mono-material" in text,
        "multifunctional": "2-in-1" in text or "multi-benefit" in text or "multi-functional" in text,
        "sensorial": "sensorial" in text or "texture" in text or "transformative" in text,
        "claims": any(w in text for w in ["hydrating", "brightening", "anti-aging", "barrier"])
    }

def score_from_flags(flags, confirmations):
    score_breakdown = []

    # Ingredient profile
    ing_score = sum([
        6 if confirmations["bio_based"] else 0,
        6 if confirmations["biotech"] else 0,
        6 if confirmations["upcycled"] else 0,
        6 if confirmations["biodegradable"] else 0,
        6 if confirmations["no_peg"] else 0
    ])
    score_breakdown.append(("Ingredient profile", ing_score, 30))

    # Formulation impact
    form_score = sum([
        10 if confirmations["cold_process"] else 0,
        10 if confirmations["waterless"] else 0,
        5
    ])
    score_breakdown.append(("Formulation impact", form_score, 25))

    # Packaging
    pack_score = sum([
        10 if confirmations["waterless"] else 0,
        10 if confirmations["refillable"] else 0
    ])
    score_breakdown.append(("Packaging", pack_score, 20))

    # Application relevance
    app_score = sum([
        5 if confirmations["multifunctional"] else 0,
        10 if confirmations["sensorial"] else 0,
        10 if confirmations["claims"] else 0
    ])
    score_breakdown.append(("Application relevance", app_score, 25))

    return score_breakdown

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Text extracted from PDF.")
    with st.expander("📝 Raw Extracted Text"):
        st.write(text)

    st.markdown("### 🧠 Auto-detected sustainability features")
    flags = detect_flags(text)

    confirmations = {}
    confirmations["bio_based"] = st.checkbox("Bio-based or botanical ingredients", value=flags["bio_based"])
    confirmations["biotech"] = st.checkbox("Biotech / fermentation origin", value=flags["biotech"])
    confirmations["upcycled"] = st.checkbox("Upcycled / side-stream valorization", value=flags["upcycled"])
    confirmations["biodegradable"] = st.checkbox("Biodegradable ingredient or material", value=flags["biodegradable"])
    confirmations["no_peg"] = st.checkbox("Free from PEGs, silicones, microplastics", value=flags["no_peg"])
    st.markdown("---")
    confirmations["cold_process"] = st.checkbox("Cold or warm process", value=flags["cold_process"])
    confirmations["waterless"] = st.checkbox("Waterless or solid format", value=flags["waterless"])
    confirmations["refillable"] = st.checkbox("Refillable or recyclable packaging", value=flags["refillable"])
    st.markdown("---")
    confirmations["multifunctional"] = st.checkbox("Multifunctional / 2-in-1 claims", value=flags["multifunctional"])
    confirmations["sensorial"] = st.checkbox("Sensorial or transformative texture", value=flags["sensorial"])
    confirmations["claims"] = st.checkbox("Claims: hydration, brightening, barrier", value=flags["claims"])

    results = score_from_flags(flags, confirmations)

    st.subheader("📊 Final Sustainability Score")
    total = sum(x[1] for x in results)
    max_total = sum(x[2] for x in results)

    for cat, val, maxval in results:
        st.write(f"**{cat}**: {val} / {maxval}")

    st.metric("🌟 SFI Score", f"{total} / {max_total}")
    if total >= 80:
        st.success("💚 Sustainably Formulated")
    elif total >= 60:
        st.info("💛 Better Choice")
    else:
        st.warning("⚠️ Needs Improvement")
