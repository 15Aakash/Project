from fpdf import FPDF
import tempfile
import re


def clean_text(text):
    replacements = {
        "•": "-",
        "–": "-",
        "—": "-",
        "-": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "≈": "~",
        "≥": ">=",
        "≤": "<=",
        "→": "->",
        "\t": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = text.replace("**", "")
    text = text.replace("---", "")

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

    if title.strip():
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(25, 25, 25)
        pdf.cell(0, 12, title, ln=True, align="C")
        pdf.ln(8)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(40, 40, 40)

    for line in content.split("\n"):
        line = clean_text(line.strip())

        if not line:
            pdf.ln(4)
            continue

        if title.strip() and line.lower() == title.lower():
            continue

        if re.match(r"^\d+\.\s+", line) or line.endswith(":"):
            pdf.ln(3)
            pdf.set_font("Arial", "B", 13)
            pdf.set_text_color(20, 40, 90)
            pdf.multi_cell(0, 8, line)
            pdf.ln(2)
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(40, 40, 40)

        elif line.startswith("- "):
            pdf.multi_cell(0, 7, "- " + line[2:])

        else:
            pdf.multi_cell(0, 7, line)

        pdf.ln(1)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)

    return temp_file.name
