from typing import Optional
from typing_extensions import TypedDict

class ProcessingState(TypedDict):
    system_name: str
    pdf_file_path: Optional[str]
    image_path: str
    extracted_text: Optional[str]
    extracted_dimensions: Optional[dict] = {}
    image_analysis: Optional[dict]
    error: Optional[str]