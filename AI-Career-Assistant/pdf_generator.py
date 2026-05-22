from fpdf import FPDF
import tempfile


def create_pdf(title, content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, title)

    pdf.ln(5)

    pdf.set_font("Arial", "", 11)

    content = content.replace("•", "-")

    for line in content.split("\n"):
        pdf.multi_cell(0, 8, line)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)

    return temp_file.name
