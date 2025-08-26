import base64
from app.services.llm_service import LLMService


async def analyze_image(state: dict, llm_service: LLMService, image_path: str) -> dict:
    try:
        # Read and encode image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        analysis = await llm_service.analyze_image_with_text(state, encoded_image)
        return {"image_analysis": analysis, "error": None}

    except Exception as e:
        return {"image_analysis": None, "error": f"Image analysis failed: {str(e)}"}