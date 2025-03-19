import pdfplumber

def extract_text_from_pdf(pdf_path):
    """ Estrae il testo da un PDF """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text
#Legge un PDF e estrae il testo