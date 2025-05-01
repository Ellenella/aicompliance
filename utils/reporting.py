from fpdf import FPDF

class PDFReport:
    @staticmethod
    def generate(text, results):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="EU Compliance Report", ln=1, align="C")
        pdf.multi_cell(0, 10, txt=f"Risk Level: {results['risk_level']}")
        return pdf.output(dest="S").encode("latin1")