from fpdf import FPDF
import tempfile


def clean_text(text):
    replacements = {
        "•": "-",
        "–": "-",
        "—": "-",
        "’": "'",
        "“": '"',
        "”": '"',
        "\t": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "ignore").decode("latin-1")


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def create_pdf(title, content, filename):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(left=20, top=18, right=20)
    pdf.add_page()

    title = clean_text(title)
    content = clean_text(content)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 11)

    for line in content.split("\n"):
        line = line.strip()

        if line.lower() == title.lower():
            continue

        if not line:
            pdf.ln(4)
            continue

        if line.endswith(":"):
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 7, line)
            pdf.set_font("Arial", "", 11)
        else:
            pdf.multi_cell(0, 7, line)

        pdf.ln(1)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)

    return temp_file.name
