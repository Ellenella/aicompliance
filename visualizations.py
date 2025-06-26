import plotly.express as px
from wordcloud import WordCloud
import streamlit as st
import numpy as np
@st.cache_data
def show_score_distribution(df):
    """Histogram of compliance scores with EU thresholds"""
    fig = px.histogram(
        df,
        x="compliance_score",
        color="status",
        title="EU Compliance Score Distribution",
        labels={"compliance_score": "Score (0-100)"},
        color_discrete_map={
            "Compliant": "#2ecc71",  # Green
            "Review": "#f39c12",     # Yellow
            "Violating": "#e74c3c"   # Red
        },
        nbins=20
    )
    # Add EU threshold lines
    fig.add_vline(x=80, line_dash="dash", line_color="#2ecc71", 
                 annotation_text="GDPR Safe Harbor")
    fig.add_vline(x=50, line_dash="dash", line_color="#f39c12",
                 annotation_text="Review Threshold")
    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def show_compliance_matrix(df):
    """Toxicity vs PII heatmap"""
    fig = px.density_heatmap(
        df,
        x="toxicity_score",
        y="pii_count",
        title="Risk Matrix (EU AI Act Article 5)",
        labels={
            "toxicity_score": "Toxicity %",
            "pii_count": "PII Items Detected"
        },
        facet_col="risk_level"
    )
    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def show_risk_pie(df):
    """EU AI Act risk categories breakdown"""
    risk_counts = df["risk_level"].value_counts().reset_index()
    fig = px.pie(
        risk_counts,
        values="count",
        names="risk_level",
        title="EU AI Act Risk Distribution",
        color="risk_level",
        color_discrete_map={
            "high": "#e74c3c",
            "medium": "#f39c12",
            "low": "#2ecc71"
        },
        hole=0.3
    )
    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def show_toxicity_bias(df):
    """Heatmap of toxicity vs bias"""
    fig = px.density_heatmap(df, x="toxicity_score", y="bias_score",
                           title="Toxicity vs. Bias Density")
    st.plotly_chart(fig)

@st.cache_data
def show_wordcloud(df):
    """Word cloud of problematic terms"""
    text = " ".join(df[df["status"] != "Compliant"]["text"])
    wordcloud = WordCloud(width=800, height=400).generate(text)
    st.image(wordcloud.to_array(), caption="Common Violation Terms")