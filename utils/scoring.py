import pandas as pd
import numpy as np
from utils.eu_ai_act import classify_risk
from utils.gdpr_utils import GDPRHandler

class ComplianceScorer:
    def __init__(self):
        self.weights = {
            'toxicity': 0.3,
            'bias': 0.3,
            'pii': 0.4
        }
        self.thresholds = {
            'compliant': 80,
            'review': 50
        }

    def calculate_scores(self, df):
        """Main scoring pipeline"""
        df = self._normalize_scores(df)
        df = self._compute_compliance(df)
        df = self._add_regulatory_flags(df)
        df['score_explanation'] = df.apply(self._explain_score, axis=1)
        return df

    def _normalize_scores(self, df):
        """Convert all scores to 0-1 scale"""
        df['toxicity_norm'] = df['toxicity_score'] / 100
        df['bias_norm'] = df['bias_score'] / 100
        df['pii_penalty'] = df['pii_detected'].apply(
            lambda x: 1 if x != "None" and x != [] else 0
        )
        return df

    def _compute_compliance(self, df):
        """Calculate composite scores with weights"""
        df['compliance_score'] = 100 * (1 - (
            self.weights['toxicity'] * df['toxicity_norm'] +
            self.weights['bias'] * df['bias_norm'] +
            self.weights['pii'] * df['pii_penalty']
        )).clip(0, 100)
        
        conditions = [
            (df['compliance_score'] >= self.thresholds['compliant']),
            (df['compliance_score'] >= self.thresholds['review']),
            (df['compliance_score'] < self.thresholds['review'])
        ]
        choices = ["Compliant", "Review", "Violating"]
        df['status'] = np.select(conditions, choices, default="Unknown")
        df['status_emoji'] = df['status'].map({
            "Compliant": "🟢",
            "Review": "🟡",
            "Violating": "🔴"
        })
        return df

    def _add_regulatory_flags(self, df):
        """Add EU regulation specific classifications"""
        df['risk_level'] = df.apply(
            lambda row: classify_risk(row['text'], row['compliance_score']/100), 
            axis=1
        )
        df['gdpr_articles_violated'] = df.apply(
            self._map_to_gdpr_articles,
            axis=1
        )
        return df

    def _map_to_gdpr_articles(self, row):
        """Identify specific GDPR violations"""
        violations = set()
        if row['pii_penalty'] > 0:
            violations.update(["Art.5(1)(f)", "Art.32"])
        if row['toxicity_norm'] > 0.7:
            violations.add("Art.22")
        if row['bias_norm'] > 0.6:
            violations.add("Art.9")
        return ", ".join(violations) if violations else "Compliant"

    def _explain_score(self, row):
        """Generate human-readable explanations"""
        explanations = []
        if row['toxicity_norm'] > 0.7:
            explanations.append(f"High toxicity ({row['toxicity_score']}%)")
        if row['pii_penalty'] > 0:
            pii_types = ", ".join(set(
                [pii.split('(')[1].strip(')') 
                 for pii in row['pii_detected'] 
                 if isinstance(pii, list)]
            ))
            explanations.append(f"PII detected ({pii_types})")
        if row['bias_norm'] > 0.6:
            explanations.append(f"Potential bias ({row['bias_score']}%)")
        return " | ".join(explanations) if explanations else "Compliant"

def calculate_compliance_score(df):
    return ComplianceScorer().calculate_scores(df)