
import json
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI

client = OpenAI(api_key="")


# ==========================
# Pydantic models
# ==========================

class Dimensions(BaseModel):
    L: float = Field(description="Length (m)")
    l: float = Field(description="Width (m)")
    H: float = Field(description="Height (m)")


class Equipment(BaseModel):
    name: str = Field(description="Equipment name")
    dimensions: Dimensions = Field(description="Dimensions in meters")
    stage: str = Field(description="Placement stage: 'ground', '1st_floor', '2nd_floor', etc.")
    stage_distance: float = Field(
        description="Distance of the stage from the ground in meters (ground=0)"
    )


class EquipmentList(BaseModel):
    equipments: List[Equipment] = Field(description="List of equipment with dimensions, stage and stage distance")


# ==========================
# Function to parse text
# ==========================


def extract_equipment_list(system_name: str, text: str) -> dict:
    schema = EquipmentList.model_json_schema()
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": f"""
                You are a strict JSON parser. 
                From the following user-provided text about a {system_name}, 
                extract all system components and return ONLY valid JSON that strictly matches this schema:
                
                {json.dumps(schema, indent=2)}
                
                Each component must include:
                - name: the component name in English (translate or infer if missing)
                - dimensions: L, W, H in meters (if not specified, estimate based on typical {system_name} components)
                - stage: ground, 1st_floor, 2nd_floor, etc. (if not specified, infer logically from common {system_name} layouts)
                - stage_distance: distance in meters from the ground (ground = 0, 1st_floor = typical 3m, 2nd_floor = 6m, etc.)
                
                If any parameter is missing, use your knowledge of {system_name} systems to provide the most reasonable value.
                
                User text:
                {input_text}
                """
            },
            {
                "role": "user",
                "content": text
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
        print(f"❌ Parsing error: {e}")
        print("Raw output:", raw_output)
        data = {"error": str(e), "raw_output": raw_output}

    return data


# ==========================
# Example usage
# ==========================

if __name__ == "__main__":
    input_text = """
    CoalPile : 150 × 50 × 15
    Pulverizer : 10 × 6 × 5
    Boiler : 35 × 30 × 70
    SCRReactor : 15 × 12 × 20
    FlyAshSystem (ESP/filtre) : 40 × 20 × 25
    SO2Scrubber (FGD, cylindre → boîte équivalente) : 22 × 22 × 36
    Stack (cheminée, cylindre → boîte équivalente) : 13 × 13 × 180
    SteamTurbine : 45 × 10 × 8
    Generator : 12 × 5 × 6
    Condenser : 25 × 8 × 6
    """
    system_name = "Coal Fired Power Station"

    result = extract_equipment_list(system_name, input_text)
    print(json.dumps(result, indent=4, ensure_ascii=False))
