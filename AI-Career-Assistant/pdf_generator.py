from fpdf import FPDF
import tempfile


def clean_text(text):
    replacements = {
        "•": "-",
        "–": "-",
        "—": "-",
        "’": "'",
        "“": '"',
        "”": '"'
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "ignore").decode("latin-1")


def create_pdf(title, content, filename):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text(title), ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", size=11)

    content = clean_text(content)

    lines = content.split("\n")

    for line in lines:

        if line.strip() == "":
            pdf.ln(4)
        else:
            pdf.multi_cell(0, 8, line)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    pdf.output(temp_file.name)

    return temp_file.name
