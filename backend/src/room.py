from pydantic import BaseModel, Field

class CreateRoom(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=100)
    min_access_level: int = Field(ge=1, le=5, default=1)
    is_active: bool = True

class UpdateRoom(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    min_access_level: int = Field(ge=1, le=5, default=1)
    is_active: bool