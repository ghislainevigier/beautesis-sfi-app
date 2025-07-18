
import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF

st.set_page_config(page_title="Beautesis Sustainable Formulation Index", layout="wide")

st.title("🌿 Beautesis Sustainable Formulation Index")
st.markdown("This tool helps assess the sustainability of any personal care formulation by analyzing key attributes — from ingredient sourcing to product format. It uses AI to pre-score, lets you confirm assumptions, and generates improvement suggestions and a downloadable summary.")

uploaded_file = st.file_uploader("📄 Upload a full formulation PDF", type=["pdf"])

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

def score_from_flags(confirmations):
    score_breakdown = []
    ing_score = sum([6 if confirmations[k] else 0 for k in ["bio_based", "biotech", "upcycled", "biodegradable", "no_peg"]])
    score_breakdown.append(("Ingredient profile", ing_score, 30))
    form_score = 10 * confirmations["cold_process"] + 10 * confirmations["waterless"] + 5
    score_breakdown.append(("Formulation impact", form_score, 25))
    pack_score = 10 * confirmations["waterless"] + 10 * confirmations["refillable"]
    score_breakdown.append(("Packaging", pack_score, 20))
    app_score = 5 * confirmations["multifunctional"] + 10 * confirmations["sensorial"] + 10 * confirmations["claims"]
    score_breakdown.append(("Application relevance", app_score, 25))
    return score_breakdown

def generate_suggestions(confirmations):
    suggestions = []
    if not confirmations["bio_based"]:
        suggestions.append("Consider using more botanical or bio-based ingredients.")
    if not confirmations["biotech"]:
        suggestions.append("Explore fermentation or biomimetic actives to enhance innovation.")
    if not confirmations["cold_process"]:
        suggestions.append("Switch to cold-process to reduce energy consumption.")
    if not confirmations["refillable"]:
        suggestions.append("Use refillable or recyclable packaging formats.")
    if not confirmations["waterless"]:
        suggestions.append("Try solid, concentrated, or waterless formats to reduce water use.")
    return suggestions

def export_pdf(score, breakdown, suggestions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Beautesis Sustainability Score Summary", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Total Score: {score} / 100", ln=True)
    pdf.ln(5)
    for cat, val, maxval in breakdown:
        pdf.cell(0, 10, f"{cat}: {val} / {maxval}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, "Suggestions for Improvement:", ln=True)
    for s in suggestions:
        pdf.multi_cell(0, 10, f"- {s}")
    pdf.output("beautesis_sfi_summary.pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Text extracted.")
    with st.expander("📝 See extracted text"):
        st.write(text)

    st.markdown("[📥 Click to download](beautesis_sfi_summary.pdf)", unsafe_allow_html=True)
    flags = detect_flags(text)
    confirmations = {}
    col1, col2 = st.columns(2)
    with col1:
        confirmations["bio_based"] = st.checkbox("🟢 Bio-based or botanical", value=flags["bio_based"])
        confirmations["biotech"] = st.checkbox("🟢 Biotech / fermentation", value=flags["biotech"])
        confirmations["upcycled"] = st.checkbox("🟢 Upcycled / side-stream", value=flags["upcycled"])
        confirmations["biodegradable"] = st.checkbox("🟢 Biodegradable", value=flags["biodegradable"])
        confirmations["no_peg"] = st.checkbox("🟢 PEG/silicone-free", value=flags["no_peg"])
    with col2:
        confirmations["cold_process"] = st.checkbox("🟢 Cold or warm process", value=flags["cold_process"])
        confirmations["waterless"] = st.checkbox("🟢 Waterless / solid", value=flags["waterless"])
        confirmations["refillable"] = st.checkbox("🟢 Refillable or recyclable", value=flags["refillable"])
        confirmations["multifunctional"] = st.checkbox("🟢 Multifunctional / 2-in-1", value=flags["multifunctional"])
        confirmations["sensorial"] = st.checkbox("🟢 Sensorial or transformative", value=flags["sensorial"])
        confirmations["claims"] = st.checkbox("🟢 Hydrating / brightening / barrier", value=flags["claims"])

    st.markdown("---")
    results = score_from_flags(confirmations)
    suggestions = generate_suggestions(confirmations)

    st.markdown("### 🧭 Final Sustainability Score")
    with st.container(border=True):
        total = sum(x[1] for x in results)
        max_total = sum(x[2] for x in results)
        for cat, val, maxval in results:
            st.write(f"**{cat}:** {val} / {maxval}")
        st.metric("🌟 SFI Score", f"{total} / {max_total}")
        if total >= 80:
            st.success("💚 Sustainably Formulated")
        elif total >= 60:
            st.info("💛 Better Choice")
        else:
            st.warning("⚠️ Needs Improvement")

    st.markdown("### 💡 Suggested Improvements")
    for s in suggestions:
        st.write("•", s)

    if st.button("📄 Download PDF Summary"):
        export_pdf(total, results, suggestions)
        st.success("PDF generated!")
        st.markdown("[📥 Click to download](sandbox:/mnt/data/beautesis_sfi_summary.pdf)", unsafe_allow_html=True)
