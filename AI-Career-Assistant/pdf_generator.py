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


def create_pdf(title, content, filename):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, clean_text(title), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    pdf.set_font("Arial", size=11)

    content = clean_text(content)

    lines = content.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            pdf.ln(5)
            continue

        try:
            pdf.multi_cell(
                190,
                8,
                line
            )

        except:
            continue

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    pdf.output(temp_file.name)

    return temp_file.name
