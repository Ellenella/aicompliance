import streamlit as st
import pandas as pd
from utils.detectors import ComplianceDetector
from utils.scoring import calculate_compliance_score
from utils.eu_ai_act import classify_risk
from utils.gdpr_utils import GDPRHandler
from utils.reporting import PDFReport
from utils.visualizations import *
import os

# App Config
st.set_page_config(
    page_title="AI Compliance Analyzer",
    layout="wide",
    page_icon="🛡️"
)

@st.cache_resource
def load_detector():
    return ComplianceDetector()

@st.cache_data
def load_regulations():
    with open("assets/eu_regulations.md", "r") as f:
        return f.read()

import numpy as np

def get_bias_score(text):
    bias_scores = detector.analyze_bias(text)
    if bias_scores:  # non-empty dict evaluates True
        return np.mean(list(bias_scores.values()))
    else:
        return 0
    
def show_compliance_guidelines():
    with st.expander("📜 EU Compliance Guidelines", expanded=False):
        st.markdown(load_regulations())

def analyze_content(content, detector):
    """Central analysis function"""
    content = content.copy()
    content["toxicity_score"] = content["text"].apply(detector.check_toxicity)
    content["pii_detected"] = content["text"].apply(detector.find_pii)
    content["bias_score"] = content["text"].apply(
    lambda t: (lambda scores: np.mean(list(scores.values())) if scores else 0)(detector.analyze_bias(t))
)
    results = calculate_compliance_score(content)
    st.write("Sample compliance_score:", results["compliance_score"].iloc[0])   
    return results

def main():
    st.title("🛡️ EU AI Compliance Analyzer")
    st.markdown("Automated detection of GDPR and EU AI Act violations")
    
    detector = load_detector()
    show_compliance_guidelines()
    
    # Input Section
    input_method = st.radio(
        "Input method:",
        ["Text Input", "CSV Upload"],
        horizontal=True
    )
    
    content = None
    if input_method == "Text Input":
        text = st.text_area("Paste AI-generated content", height=150)
        if text:
            content = pd.DataFrame([{"text": text}])
    elif input_method == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            try:
                content = pd.read_csv(uploaded_file)
                if "text" not in content.columns:
                    st.error("CSV must contain 'text' column")
            except Exception as e:
                st.error(f"Failed to process CSV: {str(e)}")

    # Analysis Tabs
    if content is not None:
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Detailed Analysis", "📝 Full Report"])
        
        with tab1:
            if st.button("Run Compliance Analysis", type="primary"):
                with st.spinner("Analyzing..."):
                    st.write("Analyzing content...")
                    st.session_state.results = analyze_content(content, detector)
                    st.write("session started!", 
                    st.session_state.results[
                        ["text","toxicity_score","pii_detected","bias_score","compliance_score", "status", "gdpr_articles_violated"]
                    ])
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Avg Score", f"{st.session_state.results['compliance_score'].mean():.1f}")
                    
                    # Visualizations
                    show_score_distribution(st.session_state.results)
                    
                    st.subheader("EU Regulatory Breakdown")
                    col_left, col_right = st.columns(2)
                    with col_left:
                        show_risk_pie(st.session_state.results)
                        st.markdown("**Risk Categories**: High, Medium, Low")
                    
                    st.warning("""
                        **EU Compliance Notes**:  
                        - Scores <50 require immediate review (GDPR Art.35)  
                        - High-risk systems need DPIA documentation  
                    """)
                    
        
        if "results" in st.session_state:
            with tab2:
                st.subheader("Detailed Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    show_toxicity_bias(st.session_state.results)
                    st.dataframe(
                        st.session_state.results[["text", "score_explanation"]],
                        height=300
                    )
                with col2:
                    try:
                        # Generate and display word cloud
                        if text.strip():
                            show_wordcloud(st.session_state.results)
                        else:
                            st.warning("No valid text available to generate a word cloud.")
                    except Exception as e:
                        st.error(f"The word cloud could not be generated because It needs more than one word: {str(e)}")
                    
                    # show_pii_trend is not defined, so this line is commented out
                    # show_pii_trend(st.session_state.results)
            
            with tab3:
                st.subheader("Regulatory Compliance Details")
                st.dataframe(
                    st.session_state.results[
                        ["text","toxicity_score","pii_detected","bias_score","compliance_score", "status", "gdpr_articles_violated"]
                    ],
                    height=400,
                    use_container_width=True
                )
                
                if "results" in st.session_state and st.checkbox("Enable GDPR Anonymization"):
                    st.session_state.results["text"] = st.session_state.results["text"].apply(GDPRHandler.anonymize)
                
                export_format = st.selectbox("Export format:", ["CSV"])
                if export_format == "CSV":
                    csv = st.session_state.results.to_csv(index=False)
                    st.download_button("Download CSV", data=csv, file_name="report.csv")
                elif export_format == "PDF":
                    pdf = PDFReport.generate(
                        text="Compliance Report",
                        results=st.session_state.results
                    )
                    st.download_button("Download PDF", data=pdf, file_name="report.pdf")

if __name__ == "__main__":
    os.makedirs("./models/saved_models", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    if not os.path.exists("assets/eu_regulations.md"):
        # Write the markdown file
        with open("assets/eu_regulations.md", "w") as f:
            f.write("### EU Compliance Reference\n\n### GDPR Key Articles\n\n### AI Act Risk Classes")

        # Conditional display
        if st.checkbox("Show EU Compliance Reference"):
            with open("assets/eu_regulations.md", "r") as f:
                st.markdown(f.read())
    main()
