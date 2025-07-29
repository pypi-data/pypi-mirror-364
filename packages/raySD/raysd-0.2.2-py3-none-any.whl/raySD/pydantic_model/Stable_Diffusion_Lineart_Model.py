from pydantic import BaseModel, model_validator
from typing import List, Dict, Any, Optional

class SD_Lineart_Config(BaseModel):
    pretrain_model_path: str = ""
    checkpoint_path: str = ""
    lora_style_path: str = ""
    style_name: str = ""
    res_ref: int = 512
    height: int = 512
    width: int = 512
    control_teed_path: str = ""
    control_lineart_path: str = ""
    teed_detector_path: str = ""
    teed_model_name: str = ""
    inference_steps: int = 20
    guidance_scale: float = 7
    control_teed_scale: float = 1.0
    control_lineart_scale: float = 1.0
    clip_skip: int = 2
    num_images_per_prompt: int = 1