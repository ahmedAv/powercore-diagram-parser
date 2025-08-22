from pydantic import BaseModel, Field
from typing import List, Optional

class Vector3(BaseModel):
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    z: float = Field(description="Z coordinate")

class Component(BaseModel):
    name: str = Field(description="Equipment name (identifier)")
    modelName: str = Field(description="Unity prefab name")
    position: Vector3 = Field(description="Local position relative to root")
    rotation: Vector3 = Field(description="Local rotation (Euler angles, deg)")
    scale: Vector3 = Field(description="Local scale")
    anchor: str = Field(description="Placement reference (e.g., 'center' / 'bottom')")

class Relation(BaseModel):
    from_id: str = Field(alias="from", description="Source equipment name")
    to: str = Field(description="Target equipment name")
    fromPosition: Vector3 = Field(description="Start point in local coordinates")
    toPosition: Vector3 = Field(description="End point in local coordinates")
    connectionType: Optional[str] = Field(default="line", description="Type of connection")
    modelName: Optional[str] = Field(default=None, description="Prefab for connection")
    rotation: Optional[Vector3] = Field(default=None, description="Rotation if connection is a 3D model")
    scale: Optional[Vector3] = Field(default=None, description="Scale if connection is a 3D model")
    fromPort: Optional[str] = Field(default=None, description="Identifier if equipment has multiple ports")
    toPort: Optional[str] = Field(default=None, description="Identifier if equipment has multiple ports")
    group: Optional[str] = Field(default=None, description="Optional grouping for visualization/hierarchy")

class DiagramAnalysis(BaseModel):
    rootPosition: Vector3 = Field(description="Origin of the scene")
    components: List[Component] = Field(description="List of equipment/components")
    relations: List[Relation] = Field(description="List of relations between equipment")