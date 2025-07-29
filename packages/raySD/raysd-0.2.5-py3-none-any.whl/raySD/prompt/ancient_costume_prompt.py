from pydantic import BaseModel, model_validator
from typing import List, Dict, Any, Optional

class AncientCostumePrompt(BaseModel):
    def __init__(self, gender: int):
        self.gender = gender
        if gender == 1:
            self.key1 = "boy"
            self.key2 = "male"
        else:
            self.key1 = "girl"
            self.key2 = "female"

        self.prompt = ""
        self.negative_prompt = ""

    def get_prompt(self):
        return self.prompt, self.negative_prompt