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


def create_pdf(title, content, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(left=20, top=18, right=20)
    pdf.add_page()

    title = clean_text(title)
    content = clean_text(content)

    # Title only ONCE, not repeated on every page
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 11)

    lines = content.split("\n")

    for line in lines:
        line = line.strip()

        # Avoid repeating title if content also starts with same title
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
            pdf.multi_cell(0, 7, line, align="J")

        pdf.ln(1)

    # Page numbers only
    total_pages = pdf.page_no()
    for page in range(1, total_pages + 1):
        pdf.page = page
        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 10, f"Page {page}", align="C")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)

    return temp_file.name
