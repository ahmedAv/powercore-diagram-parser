import PyPDF2


async def extract_text_from_pdf(state: dict) -> dict:
    try:

        pdf_path = state.get("pdf_file_path")
        if not pdf_path:
            return {"extracted_text": None, "error": "Missing 'image_path' in state"}

        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"

        return {"extracted_text": text.strip(), "error": None}

    except Exception as e:
        return {"extracted_text": None, "error": f"PDF extraction failed: {str(e)}"}