from pydantic import BaseModel, model_validator
from typing import List, Dict, Any, Optional

class ImageGenerateModel(BaseModel):
    image: str = ""
    gender: int = -1
    age: int = 0