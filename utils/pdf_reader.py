import fitz  # fitz is the import name for PyMuPDF


def extract_text_from_pdf(uploaded_file):
    """
    INPUT:  PDF file uploaded through Streamlit
    OUTPUT: Plain text string of entire resume
    """

    # Open PDF from file bytes
    # stream = file content, filetype tells fitz it's a PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    text = ""

    # Loop through every page
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()  # extract text from this page

    # Clean extra whitespace and newlines
    text = " ".join(text.split())

    return text



