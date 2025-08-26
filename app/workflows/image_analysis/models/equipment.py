from pydantic import BaseModel, Field
from typing import List

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