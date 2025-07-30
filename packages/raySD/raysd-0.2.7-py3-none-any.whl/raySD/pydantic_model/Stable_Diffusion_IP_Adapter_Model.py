from pydantic import BaseModel, model_validator
from typing import List, Dict, Any, Optional

class SD_IP_Config(BaseModel):
    pretrain_model_path: str = ""
    checkpoint_path: str = ""
    lora_style_path: str = ""
    style_name: str = ""
    height: int = 512
    width: int = 512
    ip_adapter_plus: bool = False
    version: float = 1.0
    image_encoder_path: str = ""
    ip_adapter_checkpoint_path: str = ""
    insightface_app_name: str = ""
    insightface_providers: List = []

    det_size_face: tuple = (640, 640)
    target_size: int = 224
    inference_steps: int = 20
    guidance_scale: float = 7
    ip_adapter_scale: float = 0.6
    clip_skip: int = 2
    num_images_per_prompt: int = 1
