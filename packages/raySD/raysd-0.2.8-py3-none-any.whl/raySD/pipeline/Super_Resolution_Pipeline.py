from raySD.pipeline.Abstract_Pipeline import *
from PIL import Image
import importlib
import time
import numpy as np
import cv2

class SuperResolutionPipeline(AbstractPipeline):
    def __init__(self, model_path: str, device="CPU", output_size=(768, 768)):
        super().__init__()
        self.model_path = model_path
        self.device = device
        self.output_size = output_size
        
    def load_weights(self):
        module = importlib.import_module("openvino")
        Core = getattr(module, "Core")
        core = Core()
        model_ov = core.read_model(self.model_path)
        self.model = core.compile_model(model_ov, device_name=self.device)
        print("LOAD SUPER RESOLUTION MODEL DONE")

    
    def forward(self, x: Image.Image, **kwargs)->Image.Image:
        st = time.time()
        x = np.array(x)
        x = x / 255.0
        x = np.expand_dims(x, axis=0)
        x = np.transpose(x, (0, 3, 1, 2))
        y = self.model([x])
        start_time = time.time()
        y = y[next(iter(y))]
        end_time = time.time()
        print(f"Inference ESRGAN: {end_time - start_time}s")
        y = np.transpose(y, (0, 2, 3, 1))
        y = np.squeeze(y)
        y = cv2.resize(y, self.output_size, interpolation=cv2.INTER_AREA)
        y = cv2.convertScaleAbs(y*255)
        image_out = Image.fromarray(y)
        ed = time.time()
        print(f"All time IF: {ed - st}s")
        return image_out