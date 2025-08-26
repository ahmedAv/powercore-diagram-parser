import os
from openai import AsyncOpenAI
import json
from openai import OpenAI
from app.core.config import settings
from app.workflows.image_analysis.models.equipment import EquipmentList
from app.workflows.image_analysis.models.diagram import DiagramAnalysis


client = OpenAI(api_key=settings.OPENAI_API_KEY)


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_component_dimensions(self, state):
        schema = EquipmentList.model_json_schema()
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                       You are a strict JSON parser. 
                       From the following user-provided text about a {state.get("system_name", "")}, 
                       extract all system components and return ONLY valid JSON that strictly matches this schema:

                       {json.dumps(schema, indent=2)}

                       Each component must include:
                       - name: the component name in English (translate or infer if missing)
                       - dimensions: L, W, H in meters (if not specified, estimate based on typical {state.get("system_name", "")} components)
                       - stage: ground, 1st_floor, 2nd_floor, etc. (if not specified, infer logically from common {state.get("system_name", "")} layouts)
                       - stage_distance: distance in meters from the ground (ground = 0, 1st_floor = typical 3m, 2nd_floor = 6m, etc.)

                       If any parameter is missing, use your knowledge of {state.get("system_name", "")} systems to provide the most reasonable value.

                       User text:
                       {state.get("extracted_text", "")}
                       """
                },
                {
                    "role": "user",
                    "content": state.get("extracted_text", "")
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            parsed = EquipmentList.model_validate_json(raw_output)
            data = parsed.model_dump()
        except Exception as e:
            print(f"Parsing error: {e}")
            print("Raw output:", raw_output)
            data = {"error": str(e), "raw_output": raw_output}

        return data

    async def analyze_image_with_text(self, state, encoded_image: str):
        # Create the prompt with JSON schema
        json_schema = DiagramAnalysis.model_json_schema()

        # Send request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an expert diagram analyzer. 
                        Your task is to extract components and relations from a diagram and return them in JSON format 
                        that strictly follows the PowerCore specification.

                        You MUST return valid JSON that matches this schema:
                        {json.dumps(json_schema, indent=2)}

                        Here is the list of component dimensions extracted from text:
                        {json.dumps(state.get("extracted_dimensions", {}), indent=2)}

                        Important rules:
                        - Use 3D coordinates (x, y, z)
                        - Always include rootPosition as the origin of the scene
                        - Each component must have: name, modelName, position, rotation, scale, anchor
                        - Each relation must have: from, to, fromPosition, toPosition
                        - rotation, scale, and modelName are optional for relations (only if using 3D prefab connections)
                        - Use clear and consistent names for components and relations
                        - Place each component accurately in space based on its real-world measurements.
                        - If explicit distances between components are not provided, infer logical spacing and layout 
                          using your domain knowledge and engineering reasoning.
                        - Use your domain knowledge and engineering reasoning to make reasonable assumptions 
                          about positions, orientations, and relations where information is missing.

                        FLOOR LEVEL REFERENCE:
                        - Ground floor: z = 0
                        - Adjust z-position based on equipment anchor point (typically 'ground')

                        Note: Always prioritize the real equipment data when available. Only use your domain knowledge to fill in missing information.
                        """
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this diagram and return the components (3D) and their relations in PowerCore JSON format."
                                    "Pay special attention to vertical positioning (z-axis) based on floor levels (ground, 1st floor, etc.)."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        # Get model output
        raw_output = response.choices[0].message.content.strip()

        # Parse and validate using Pydantic
        try:
            parsed_data = DiagramAnalysis.model_validate_json(raw_output)
            data = parsed_data.model_dump(by_alias=True)
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            print("Raw output was:")
            print(raw_output)
            data = {"error": str(e), "raw_output": raw_output}

        return data