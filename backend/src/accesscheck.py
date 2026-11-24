from pydantic import BaseModel, Field

class AccessCheckRequest(BaseModel):
    card_id: str = Field(min_length=4, max_length=64)
    room_code: str = Field(min_length=2, max_length=32)