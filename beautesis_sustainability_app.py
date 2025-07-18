
# beautesis_sustainability_app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Beautesis Sustainability Scorer", layout="wide")
st.title("🌿 Beautesis Sustainable Formulation Index (SFI)")
st.markdown("Upload your formulation file to generate a sustainability score and get improvement suggestions.")

uploaded_file = st.file_uploader("📄 Upload your formulation (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded and parsed successfully!")
        st.dataframe(df)

        score = 0
        total = 100
        advisory = []

        noi_criteria = any("hyaluronate" in str(i).lower() or "natural" in str(i).lower() for i in df["INCI"])
        if noi_criteria:
            score += 10
        else:
            advisory.append("Consider increasing natural or biobased ingredients to improve NOI.")

        upcycled_or_biotech = any("ferment" in str(i).lower() or "biotech" in str(i).lower() for i in df["INCI"])
        if upcycled_or_biotech:
            score += 5
        else:
            advisory.append("Explore using biotech or upcycled ingredients.")

        petrochemicals = any("PEG" in str(i) or "dimethicone" in str(i).lower() for i in df["INCI"])
        if not petrochemicals:
            score += 10
        else:
            advisory.append("Reduce reliance on petrochemical derivatives like PEG or silicones.")

        if "cold" in df.columns.str.lower().tolist():
            score += 5
        advisory.append("Indicate cold-process compatibility for bonus points.")

        if df["Wt %"].apply(lambda x: isinstance(x, (float, int)) and x < 2).sum() > 5:
            score += 5
        else:
            advisory.append("Consider using more high-efficiency actives (usage < 2%).")

        score += 5
        advisory.append("Ensure to specify packaging format (solid, refillable, recyclable) to gain full score.")

        keywords = ["brightening", "hydrating", "fast", "multifunction", "barrier", "sensorial"]
        if any(any(k in str(f).lower() for k in keywords) for f in df["Function"]):
            score += 15
        else:
            advisory.append("Add multifunctional or wellness-related claims for higher application relevance score.")

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

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
