import numpy as np
import torch
from raySD.utils.Enable_xFormers import *
from raySD.pipeline.Abstract_Pipeline import *
from raySD.prompt.chibi_prompt import *
from raySD.pydantic_model.Stable_Diffusion_IP_Adapter_Model import *
import time
import cv2
from PIL import Image
import importlib

class StableDiffusionIPAdapterPipeline(AbstractPipeline):
    def __init__(self, **kwargs):
        super().__init__()
        ## Config
        self.config = SD_IP_Config(**kwargs)

    def update_params_infer(self, **kwargs):
        self.config.inference_steps = kwargs.get("inference_steps", 20)
        self.config.guidance_scale = kwargs.get("guidance_scale", 7)
        self.config.ip_adapter_scale = kwargs.get("ip_adapter_scale", 1)
        self.config.clip_skip=kwargs.get("clip_skip", 2)
        self.config.num_images_per_prompt=kwargs.get("num_images_per_prompt", 1)

    def load_weights(self):
        from diffusers import DPMSolverMultistepScheduler
        from diffusers import StableDiffusionPipeline
        
        ## Device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DEVICE: {self.device}")
        
        ## Load Stable Diffusion model
        pipeline = StableDiffusionPipeline.from_single_file(
            self.config.checkpoint_path,
            torch_dtype=torch.float16,
            safety_checker=None
        ).to(self.device)

        ### Scheduler
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            pipeline.scheduler.config,
            algorithm_type="dpmsolver++",       # <-- DPM++
            use_karras_sigmas=True,             # <-- Karras
            solver_order=2                      # <-- 2M (2nd order multistep)
        )

        if self.config.lora_style_path:
            pipeline.load_lora_weights(self.config.lora_style_path)

        enable_xformers_if_available(pipeline)
        
        ### Load pipeline to IPAdapter
        if self.config.ip_adapter_plus:
            from ip_adapter.ip_adapter_faceid import IPAdapterFaceIDPlus
            self.ip_adapter = IPAdapterFaceIDPlus(
                pipeline,
                image_encoder_path=self.config.image_encoder_path,
                ip_ckpt=self.config.ip_adapter_checkpoint_path,
                device=self.device
            )   
        else:
            from ip_adapter.ip_adapter_faceid import IPAdapterFaceID
            self.ip_adapter = IPAdapterFaceID(
                pipeline,
                ip_ckpt=self.config.ip_adapter_checkpoint_path,
                device=self.device
            )

        module = importlib.import_module("insightface.app")
        # Load Face Analysis
        self.face_app = module.FaceAnalysis(name=self.config.insightface_app_name, providers=self.config.insightface_providers)
        self.face_app.prepare(ctx_id=0, det_size=self.config.det_size_face)
        
        module_util = importlib.import_module("insightface.utils")
        self.face_align = getattr(module_util, "face_align")

        print("LOAD SD PIPELINE DONE")

    def forward(self, x: Image.Image, **kwargs)->Image.Image:
        img = cv2.cvtColor(np.array(x), cv2.COLOR_RGB2BGR)
        faces = self.face_app.get(img)
        face_emb = torch.from_numpy(faces[0].normed_embedding).unsqueeze(0).to(self.device)
        aligned_face = self.face_align.norm_crop(img, landmark=faces[0].kps, image_size=self.config.target_size)

        print(face_emb.shape)
        print(aligned_face.shape)
        
        gender = kwargs["gender"]
        age = kwargs["age"]

        if self.config.style_name == "chibi_style":
            chibi_prompt = ChibiPrompt2(gender=gender)
            self.prompt, self.negative_prompt = chibi_prompt.get_prompt()
        
        start_time = time.time()
        image = self.ip_adapter.generate(
            face_image=aligned_face,
            faceid_embeds=face_emb,
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            guidance_scale=self.config.guidance_scale,
            num_inference_steps=self.config.inference_steps,
            scale=self.config.ip_adapter_scale,
            num_samples=self.config.num_images_per_prompt,
            width=self.config.width,
            height=self.config.height,
        )[0]
        end_time = time.time()
        print(f"Inference time: {end_time - start_time:.2f} seconds")
        return image




