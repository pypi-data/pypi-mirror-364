from pydantic import BaseModel, Field

class ImageResponseModel(BaseModel):
    image: str = ""