from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    card_id: str = Field(min_length=4, max_length=64)
    access_level: int = Field(ge=1, le=5, default=1)
    is_active: bool = True

class UpdateUser(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    access_level: int = Field(ge=1, le=5)
    is_active: bool
