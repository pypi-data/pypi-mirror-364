from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    message: str = ""