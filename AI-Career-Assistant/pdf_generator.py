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

    text = text.encode("latin-1", "ignore").decode("latin-1")

    return text


class PDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 18)
        self.set_text_color(30, 30, 30)
        self.cell(0, 12, self.title_text, ln=True, align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            10,
            f"Page {self.page_no()}",
            align="C"
        )


def create_pdf(title, content, filename):

    pdf = PDF()

    pdf.title_text = clean_text(title)

    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.add_page()

    pdf.set_left_margin(18)
    pdf.set_right_margin(18)

    pdf.set_font("Arial", size=12)

    content = clean_text(content)

    paragraphs = content.split("\n")

    for para in paragraphs:

        para = para.strip()

        if not para:
            pdf.ln(6)
            continue

        pdf.multi_cell(
            0,
            8,
            para
        )

        pdf.ln(2)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    pdf.output(temp_file.name)

    return temp_file.name
