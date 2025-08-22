

#####################
import base64
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

# Initialize client
client = OpenAI(api_key="sk-svcacct-TlgBYJ-A7AViNWRTAvUam4-18-KceIUL5V3uOtnQOvIAiaLjwX5nzhduaxi7duNq52N_t0XT3BlbkFJ7GAlu0kewliG2aNOzmQefpDod50BCWH1h0pxTbrySiJfpM-moBnQLjQDhoWOjZO9V25juAA")


# Pydantic models for structured output
class Position(BaseModel):
    x: int = Field(description="X coordinate of the component")
    y: int = Field(description="Y coordinate of the component")


class Component(BaseModel):
    id: str = Field(description="Unique identifier for the component (lowercase, no spaces)")
    name: str = Field(description="Display name of the component")
    position: Position = Field(description="Position coordinates of the component")


class Relation(BaseModel):
    from_id: str = Field(alias="from", description="Source component ID")
    to: str = Field(description="Target component ID")
    flow: Optional[str] = Field(default=None, description="Type of flow or connection")


class DiagramAnalysis(BaseModel):
    components: List[Component] = Field(description="List of components in the diagram")
    relations: List[Relation] = Field(description="List of relations between components")


def image_to_json(image_path: str, output_json: str = "components_relations.json"):
    # Encode image to base64
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Create the prompt with JSON schema
    json_schema = DiagramAnalysis.model_json_schema()

    # Send request to OpenAI
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert diagram analyzer. Extract components with their positions and relations from the diagram.

                You MUST return valid JSON that matches this schema:
                {json.dumps(json_schema, indent=2)}

                Guidelines:
                - Estimate x,y coordinates based on visual position (0,0 = top-left)
                - Use meaningful IDs (lowercase, no spaces)
                - Include all visible connections as relations
                - If flow type is not visible, omit the 'flow' field"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this diagram and extract all components with their positions (x,y coordinates) and relations between them."
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
        print(f"Error parsing JSON: {e}")
        print("Raw output was:")
        print(raw_output)
        data = {"error": str(e), "raw_output": raw_output}

    # Save to file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ JSON saved to {output_json}")
    return data


# Alternative version with retry logic for parsing errors
def image_to_json_with_retry(image_path: str, output_json: str = "components_relations.json", max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            data = image_to_json(image_path, output_json)
            if "error" not in data:
                return data
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
    return None


# Example usage
if __name__ == "__main__":
    result = image_to_json("images/4.png")

