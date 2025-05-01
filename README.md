# 🛡️ EU AI Compliance Analyzer

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://yourapp.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automated detection of GDPR and EU AI Act violations in AI-generated content, with specialized support for Italian regulations.

![Dashboard Screenshot](docs/screenshot.png)

## Features

- **Multi-Format Input**: Analyze text, CSV, or JSON inputs
- **Comprehensive Detection**:
  - ✅ Toxicity (using `unitary/toxic-bert`)
  - ✅ Bias (zero-shot classification)
  - ✅ PII (Stanza NLP + regex)
- **Regulatory Alignment**:
  - GDPR Article 5/17/22 compliance
  - EU AI Act risk classification
  - Italian Garante Privacy guidelines
- **Professional Reporting**:
  - Interactive visualizations
  - PDF/CSV/JSON exports
  - Audit-ready documentation

```mermaid
graph LR
    A[Text/CSV/JSON] --> B{Detection Engine}
    B -->|Toxicity| C[unitary/toxic-bert]
    B -->|Bias| D[Zero-shot Classifier]
    B -->|PII| E[Stanza NLP]
    C --> F[Compliance Scoring]
    D --> F
    E --> F
    F --> G[[Dashboard]]
    F --> H[[PDF Reports]]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style G fill:#9f9,stroke:#333
    style H fill:#9f9,stroke:#333
```
    
## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/ai-compliance-analyzer.git
cd ai-compliance-analyzer

# Install dependencies
pip install -r requirements.txt

# Download language models
python -m stanza download en it

# Launch app
streamlit run app.py
