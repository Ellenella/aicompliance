import plotly.express as px
from wordcloud import WordCloud
import streamlit as st
import numpy as np
@st.cache_data
def show_score_distribution(df):
    """Histogram of compliance scores"""
    fig = px.histogram(df, x="compliance_score", 
                      color="status",
                      title="Compliance Score Distribution",
                      labels={"compliance_score": "Score (0-100)"})
    st.plotly_chart(fig)
@st.cache_data
def show_risk_categories(df):
    """Donut chart of risk levels"""
    risk_counts = df["risk_level"].value_counts()
    fig = px.pie(risk_counts, names=risk_counts.index, 
                hole=0.3, title="Risk Category Distribution")
    st.plotly_chart(fig)
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

# Add other visualization functions as needed...