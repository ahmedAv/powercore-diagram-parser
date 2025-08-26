from app.services.llm_service import LLMService


async def extract_dimensions(state: dict, llm_service: LLMService) -> dict:
    try:
        text = state["extracted_text"]
        if not text:
            return {"extracted_dimensions": {}, "error": "No text to process"}
        dimensions = await llm_service.extract_component_dimensions(state)
        return {"extracted_dimensions": dimensions, "error": None}

    except Exception as e:
        return {"extracted_dimensions": None, "error": f"Dimension extraction failed: {str(e)}"}

    