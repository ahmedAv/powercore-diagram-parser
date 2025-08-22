import base64
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

# Initialize client
client = OpenAI(
    api_key="sk-svcacct-TlgBYJ-A7AViNWRTAvUam4-18-KceIUL5V3uOtnQOvIAiaLjwX5nzhduaxi7duNq52N_t0XT3BlbkFJ7GAlu0kewliG2aNOzmQefpDod50BCWH1h0pxTbrySiJfpM-moBnQLjQDhoWOjZO9V25juAA")


# ==========================
# Pydantic models (adapted)
# ==========================

class Dimensions(BaseModel):
    L: float = Field(description="Length (m)")
    l: float = Field(description="Width (m)")
    H: float = Field(description="Height (m)")

class Vector3(BaseModel):
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    z: float = Field(description="Z coordinate")


class Component(BaseModel):
    name: str = Field(description="Equipment name (identifier)")
    modelName: str = Field(description="Unity prefab name")
    position: Vector3 = Field(description="Local position relative to root")
    rotation: Vector3 = Field(description="Local rotation (Euler angles, deg)")
    dimensions: Dimensions = Field(description="Dimensions in meters")
    scale: Vector3 = Field(description="Local scale")
    anchor: str = Field(description="Placement reference (e.g., 'center' / 'bottom')")


class Relation(BaseModel):
    from_id: str = Field(alias="from", description="Source equipment name")
    to: str = Field(description="Target equipment name")
    fromPosition: Vector3 = Field(description="Start point in local coordinates")
    toPosition: Vector3 = Field(description="End point in local coordinates")
    connectionType: Optional[str] = Field(default="line", description="Type of connection (line, pipe, arrow, etc.)")
    modelName: Optional[str] = Field(default=None, description="Prefab for connection (if 3D model)")
    rotation: Optional[Vector3] = Field(default=None, description="Rotation if connection is a 3D model")
    scale: Optional[Vector3] = Field(default=None, description="Scale if connection is a 3D model")
    fromPort: Optional[str] = Field(default=None, description="Identifier if equipment has multiple ports")
    toPort: Optional[str] = Field(default=None, description="Identifier if equipment has multiple ports")
    group: Optional[str] = Field(default=None, description="Optional grouping for visualization/hierarchy")


class DiagramAnalysis(BaseModel):
    rootPosition: Vector3 = Field(description="Origin of the scene (reference point for all coordinates)")
    components: List[Component] = Field(description="List of equipment/components")
    relations: List[Relation] = Field(description="List of relations between equipment")


# ==========================
# Main extraction function
# ==========================

def image_to_json(image_path: str, output_json: str = "components_relations.json"):
    # Encode image to base64
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Create the prompt with JSON schema
    json_schema = DiagramAnalysis.model_json_schema()
    components_json = {
        "equipments": [
            {"name": "Coal Pile", "dimensions": {"L": 50.0, "W": 50.0, "H": 150.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "Pulverizer", "dimensions": {"L": 10.0, "W": 6.0, "H": 5.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "Boiler", "dimensions": {"L": 35.0, "W": 30.0, "H": 70.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "SCR Reactor", "dimensions": {"L": 15.0, "W": 12.0, "H": 20.0}, "stage": "1st_floor",
             "stage_distance": 3.0},
            {"name": "Fly Ash System (ESP/filter)", "dimensions": {"L": 40.0, "W": 20.0, "H": 25.0},
             "stage": "1st_floor", "stage_distance": 3.0},
            {"name": "SO2 Scrubber (FGD)", "dimensions": {"L": 22.0, "W": 22.0, "H": 36.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "Stack", "dimensions": {"L": 13.0, "W": 13.0, "H": 180.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "Steam Turbine", "dimensions": {"L": 45.0, "W": 10.0, "H": 8.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "Generator", "dimensions": {"L": 12.0, "W": 5.0, "H": 6.0}, "stage": "ground",
             "stage_distance": 0.0},
            {"name": "Condenser", "dimensions": {"L": 25.0, "W": 8.0, "H": 6.0}, "stage": "ground",
             "stage_distance": 0.0}
        ]
    }

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
                {json.dumps(components_json, indent=2)}

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
                            "url": f"data:image/png;base64,{image_base64}"
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

    # Save to file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ JSON saved to {output_json}")
    return data


# ==========================
# Example usage
# ==========================
if __name__ == "__main__":
    result = image_to_json("images/5.jpg")
