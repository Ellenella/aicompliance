import stanza
from transformers import pipeline
import re
import streamlit as st
class ComplianceDetector:
    def __init__(self):
        # Initialize Stanza pipeline
        stanza.download('en')  # Download English models
        self.nlp = stanza.Pipeline('en', processors='tokenize,ner')
        
        # Other models
        self.toxicity_model = pipeline("text-classification", model="unitary/toxic-bert")

    import stanza
from transformers import pipeline
import re
import torch
from typing import List, Dict, Union

class ComplianceDetector:
    def __init__(self):
        # Initialize models with caching
        self.nlp = self.load_stanza()
        self.toxicity_model = self.load_toxicity_model()
        self.bias_model = self.load_bias_model()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @st.cache_resource
    def load_stanza(_self):
        stanza.download('en')
        return stanza.Pipeline('en', processors='tokenize,ner')

    @st.cache_resource
    def load_toxicity_model(_self):
        return pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            device=0 if torch.cuda.is_available() else -1
        )

    @st.cache_resource
    def load_bias_model(_self):
        return pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )

    def check_toxicity(self, text: str) -> float:
        """
        Analyze text for toxicity using multilingual model
        Returns toxicity probability (0-100)
        """
        try:
            results = self.toxicity_model(text)
            toxic_score = next(
                (r['score'] for r in results if r['label'] == 'toxic'),
                0.0
            )
            return round(toxic_score * 100, 2)
        except Exception as e:
            print(f"Toxicity analysis error: {e}")
            return 0.0

    def analyze_bias(self, text: str) -> Dict[str, float]:
        """
        Detect bias types with zero-shot classification
        Returns dictionary with bias categories and scores
        """
        bias_categories = [
            "gender bias", 
            "racial bias",
            "religious bias",
            "age discrimination",
            "disability discrimination",
            "geographic bias"
        ]
        
        try:
            result = self.bias_model(
                text,
                candidate_labels=bias_categories,
                multi_label=True
            )
            return {
                label: round(score * 100, 2)
                for label, score in zip(result['labels'], result['scores'])
                if score > 0.3  # Only return significant biases
            }
        except Exception as e:
            print(f"Bias analysis error: {e}")
            return {}

    def find_pii(self, text):
        """Detect PII using Stanza's NER"""
        doc = self.nlp(text)
        pii_types = []
        
        for ent in doc.ents:
            if ent.type in ["PERSON", "EMAIL", "PHONE", "ORGANIZATION", "GPE", "LOCATION", "DATE", "TIME", "MONEY"]:
                pii_types.append(f"{ent.text} ({ent.type})")

         # Regex-based detection
        email_matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        phone_matches = re.findall(r"\+?\d[\d\-\(\) ]{7,}\d", text)
        url_matches = re.findall(r"https?://[^\s]+", text)
        file_path_matches = re.findall(r"(?:[a-zA-Z]:\\|/)?(?:[\w\-\.]+[/\\])+[\w\-\.]+", text)
        api_key_matches = re.findall(r"\b(?:sk|api|key|token)[\-_]?[a-z0-9]{10,}\b", text, re.IGNORECASE)

        # Add all matches to pii_types
        pii_types.extend([f"{e} (EMAIL)" for e in email_matches])
        pii_types.extend([f"{p} (PHONE)" for p in phone_matches])
        pii_types.extend([f"{u} (URL)" for u in url_matches])
        pii_types.extend([f"{f} (FILE_PATH)" for f in file_path_matches])
        pii_types.extend([f"{k} (POTENTIAL_API_KEY)" for k in api_key_matches])

        return pii_types if pii_types else "None"