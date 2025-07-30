from pydantic import BaseModel, model_validator
from typing import List, Dict, Any, Optional

class ChibiPrompt():
    def __init__(self, gender: int):
        self.gender = gender
        if gender == 1:
            self.key1 = "boy"
            self.key2 = "male"
        else:
            self.key1 = "girl"
            self.key2 = "female"

        # self.prompt = f"chibi style, solo, looking at viewer, simple background, brown hair, blue shirt, 1{self.key1}, {self.key2} focus, brown hair, warm and friendly expression, natural smile, well-aligned teeth, realistic lips, smooth facial features, expressive eyes, soft lighting, high-quality shading, professional rendering, best quality, high resolution, portrait, blue background, natural proportions, detailed face, gentle grin"
        # self.negative_prompt = f"worst quality, low quality, normal quaworst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad smile, bad anatomylity, jpeg artifacts, signature, watermark, username, blurry, bad anatomy, blurry teeth, deformed teeth, extra teeth, missing teeth"

        self.prompt = f"chibi style, solo, looking at viewer, simple background, brown hair, blue shirt, 1{self.key1},  {self.key2} (20-30 years old), {self.key2} focus, brown hair, warm and friendly expression, natural smile, well-aligned teeth, realistic lips, smooth facial features, expressive eyes, soft lighting, high-quality shading, professional rendering, best quality, high resolution, portrait, blue background, natural proportions, detailed face, gentle grin"
        self.negative_prompt = f"worst quality, low quality, normal quaworst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad smile, bad anatomylity, jpeg artifacts, signature, watermark, username, blurry, bad anatomy, blurry teeth, deformed teeth, extra teeth, missing teeth"

    def get_prompt(self):
        return self.prompt, self.negative_prompt
    

class ChibiPrompt1():
    def __init__(self, gender: int):
        self.gender = gender
        if gender == 1:
            self.key1 = "boy"
            self.key2 = "male"
        else:
            self.key1 = "girl"
            self.key2 = "female"

        self.prompt = f"chibi style, solo, 1{self.key1}, blue shirt, brown hair, looking at viewer, warm and friendly expression, natural smile, realistic lips, well-aligned teeth, smooth facial features, expressive eyes, soft lighting, detailed face, gentle grin, portrait, blue background, simple background, professional rendering, high-quality shading, bright face, soft glow, best quality, high resolution"
        self.negative_prompt = f"worst quality, low quality, normal quaworst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad smile, bad anatomylity, jpeg artifacts, signature, watermark, username, blurry, bad anatomy, blurry teeth, deformed teeth, extra teeth, missing teeth"

    def get_prompt(self):
        return self.prompt, self.negative_prompt


class ChibiPrompt2():
    def __init__(self, gender: int):
        self.gender = gender
        if gender == 1:
            self.key1 = "boy"
            self.key2 = "male"
        else:
            self.key1 = "girl"
            self.key2 = "female"

        self.prompt = f"chibi style, solo, 1{self.key1}, looking at viewer, blue shirt, friendly expression, natural smile, smooth fair skin, realistic lips, big round eyes, bright eyes, evenly lit bright face, soft glow, ambient diffuse light, high quality shading, detailed soft face, professional render, best quality, high resolution, blue background"

        self.negative_prompt = f"worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry, bad smile, bad anatomy, blurry teeth, deformed teeth, extra teeth, missing teeth, uneven lighting, harsh shadow, flat shading, discolored skin, dark chin, underexposed face, unnatural skin tone, narrow eyes, slit eyes, squinting eyes, closed eyes, color bleeding, blue tint on face"

    def get_prompt(self):
        return self.prompt, self.negative_prompt