from pydantic import BaseModel


class UserRequest(BaseModel):
    userID: str
    longitude: float
    latitude: float
