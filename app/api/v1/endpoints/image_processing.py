from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.workflows.image_analysis.graph import ImageAnalysisGraph
import tempfile
import os
from typing import Optional

router = APIRouter()


@router.post("/process-image/")
async def process_image(
        image_file: UploadFile = File(..., description="Required image file for analysis"),
        pdf_file: UploadFile | str = None,
        system_name: str = Query("Industrial System", description="Name of the system being analyzed")
):
    try:
        # Save uploaded PDF temporarily if provided
        pdf_path = None
        if pdf_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                content = await pdf_file.read()
                tmp_pdf.write(content)
                pdf_path = tmp_pdf.name

        # Save uploaded image (required)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
            img_content = await image_file.read()
            tmp_img.write(img_content)
            image_path = tmp_img.name

        # Process with LangGraph
        graph = ImageAnalysisGraph(system_name=system_name)
        result = await graph.process(system_name, image_path, pdf_path)

        # Clean up
        if pdf_path:
            os.unlink(pdf_path)
        os.unlink(image_path)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return result.get("image_analysis"),

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
